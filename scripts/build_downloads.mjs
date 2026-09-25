/**
 * build_downloads.mjs — 產生 /changelog/ 提供下載的全文檔（HTML／PDF／Markdown，皆只有中文）。
 *
 * 產出放在 `public/archive/<archive>.{html,pdf,md}`，`<archive>` 取自 src/config/br-versions.ts
 * 該版本的 `archive` 欄位（不含副檔名）。檔案進版控；pre-push 會用 scripts/lint_downloads.py
 * 檢查最新版的下載檔有沒有跟上章節內容——**潤稿後要推之前，重跑這支再一起 commit**。
 *
 * 用法：
 *   node scripts/build_downloads.mjs                    # 最新版：npm run build → HTML → Markdown → PDF → 蓋章
 *   node scripts/build_downloads.mjs --skip-build       # 已經 build 過，dist/ 是最新的
 *   node scripts/build_downloads.mjs --archived 2.2.7   # 舊版：從 gitTag 取當時的章節檔重出 Markdown，
 *                                                       # 由既有 HTML 印 PDF（HTML 已發布，不重出）
 */
import { readFileSync, existsSync, mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { resolve, dirname, join, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
const flag = (name) => argv.includes(`--${name}`);
function arg(name) {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 ? argv[i + 1] : undefined;
}

function run(cmd, args, opts = {}) {
  console.log(`\n$ ${cmd} ${args.join(' ')}`);
  const res = spawnSync(cmd, args, { cwd: ROOT, stdio: 'inherit', ...opts });
  if (res.error) throw res.error;
  if (res.status !== 0) throw new Error(`${cmd} 失敗（exit ${res.status}）`);
}

function python() {
  for (const py of ['python', 'python3', 'py']) {
    if (spawnSync(py, ['--version'], { stdio: 'ignore', shell: process.platform === 'win32' }).status === 0) return py;
  }
  throw new Error('找不到 python（蓋章需要 scripts/lint_downloads.py）');
}

// ---- 讀 br-versions.ts（regex，同 lint_downloads.py） -------------------------
const ts = readFileSync(join(ROOT, 'src/config/br-versions.ts'), 'utf8');
const versions = [...ts.slice(ts.indexOf('export const brVersions')).matchAll(/\{([^{}]*)\}/g)]
  .map((m) => Object.fromEntries([...m[1].matchAll(/^\s*(\w+):\s*'([^']*)'/gm)].map((f) => [f[1], f[2]])))
  .filter((v) => v.version);
if (versions.length === 0) throw new Error('br-versions.ts 讀不到任何版本列');

const archivedVersion = arg('archived');
const entry = archivedVersion ? versions.find((v) => v.version === archivedVersion) : versions[0];
if (!entry) throw new Error(`br-versions.ts 沒有 v${archivedVersion}`);
if (!entry.archive) throw new Error(`v${entry.version} 在 br-versions.ts 沒有 archive 欄位，請先補上檔名（不含副檔名）`);

const base = `public/archive/${entry.archive}`;
mkdirSync(join(ROOT, 'public/archive'), { recursive: true });

if (!archivedVersion) {
  // ---- 最新版 ------------------------------------------------------------------
  if (!flag('skip-build')) run('npm', ['run', 'build'], { shell: process.platform === 'win32' });
  run(process.execPath, ['scripts/export_chapters_html.mjs', '--chapters', 'all', '--out', `${base}.html`]);
  run(process.execPath, ['scripts/export_markdown.mjs', '--out', `${base}.md`]);
  run(process.execPath, ['scripts/export_pdf.mjs', '--in', `${base}.html`, '--out', `${base}.pdf`]);
  run(python(), ['scripts/lint_downloads.py', '--write'], {
    shell: process.platform === 'win32',
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
  });
} else {
  // ---- 舊版：章節檔從 git tag 取 ------------------------------------------------
  if (entry.version === versions[0].version) throw new Error('--archived 用於已歸檔版本；最新版請不帶參數');
  if (!entry.gitTag) throw new Error(`v${entry.version} 沒有 gitTag，取不到當時的章節檔`);
  if (!existsSync(join(ROOT, `${base}.html`))) throw new Error(`找不到 ${base}.html`);

  const tmp = mkdtempSync(join(tmpdir(), 'br-archived-'));
  try {
    const list = spawnSync('git', ['ls-tree', '-r', '--name-only', entry.gitTag, 'src/content/br/'], {
      cwd: ROOT,
      encoding: 'utf8',
    });
    if (list.status !== 0) throw new Error(`git ls-tree ${entry.gitTag} 失敗：${list.stderr}`);
    const paths = list.stdout.split('\n').filter((p) => p.endsWith('.md'));
    // 一次 cat-file --batch 取完所有檔（逐檔 git show 要開 400 多個行程）
    const batch = spawnSync('git', ['cat-file', '--batch'], {
      cwd: ROOT,
      input: paths.map((p) => `${entry.gitTag}:${p}`).join('\n') + '\n',
      maxBuffer: 256 * 1024 * 1024,
    });
    if (batch.status !== 0) throw new Error(`git cat-file 失敗：${batch.stderr}`);
    const buf = batch.stdout;
    let pos = 0;
    for (const p of paths) {
      const nl = buf.indexOf(0x0a, pos);
      const header = buf.subarray(pos, nl).toString();
      const size = Number(header.split(' ')[2]);
      if (!Number.isFinite(size)) throw new Error(`git cat-file 回應無法解析：${header}`);
      writeFileSync(join(tmp, basename(p)), buf.subarray(nl + 1, nl + 1 + size));
      pos = nl + 1 + size + 1;
    }
    console.log(`從 ${entry.gitTag} 取出 ${paths.length} 個章節檔`);
    run(process.execPath, ['scripts/export_markdown.mjs', '--src', tmp, '--version', entry.version, '--out', `${base}.md`]);
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
  run(process.execPath, ['scripts/export_pdf.mjs', '--in', `${base}.html`, '--out', `${base}.pdf`]);
}

console.log(`\n✔ v${entry.version} 下載檔已產生：${base}.{html,pdf,md}`);
