// 版本資料的單一推導點：build 時算出「上游最新版」與「本站發布版」，
// 供版本徽章（spec §4.1）、版本歷程頁與各章節頁使用。
//
// ## 兩個版本號，不要混為一談
//
//   上游最新版  ← `web-spec-doc/BR.md` 的 front-matter（cabforum 在 GitHub 的原文）
//   本站發布版  ← `src/config/br-versions.ts` 的 brVersions[0]
//
// 升版流程中這兩個必然會有一段時間不同（原文已抓下來、譯稿還沒跟上），此時徽章
// 顯示「落後」。**上游版本絕不可拿來當本站版本顯示**——那會讓客服以為站上內容
// 已經是新版。
//
// 章節檔的 `original_version` 是否與 brVersions[0] 一致，由
// `scripts/lint_version_consistency.py` 於 push 前把關（見 RUNBOOK §2.4）。

// 以 Vite 的 `?raw` 匯入原文，而非 node:fs——免裝 @types/node，且 Vite 會把 BR.md
// 納入依賴追蹤（改了原文，dev 會自動重載）。
import brMdRaw from '../../web-spec-doc/BR.md?raw';
import { brVersions, type BrVersionEntry } from '../config/br-versions';

const MONTHS: Record<string, string> = {
  jan: '01', feb: '02', mar: '03', apr: '04', may: '05', jun: '06',
  jul: '07', aug: '08', sep: '09', oct: '10', nov: '11', dec: '12',
};

/** BR.md 標頭的 `19-May-2026` → `2026-05-19`；認不得就回傳 null，不要猜。 */
export function parseBrDate(raw: string): string | null {
  const m = /^(\d{1,2})-([A-Za-z]{3,})-(\d{4})$/.exec(raw.trim());
  if (!m) return null;
  const mon = MONTHS[m[2].slice(0, 3).toLowerCase()];
  if (!mon) return null;
  return `${m[3]}-${mon}-${m[1].padStart(2, '0')}`;
}

export interface UpstreamInfo {
  /** 上游最新版本號，如 "2.2.9"；讀不到時為 null */
  version: string | null;
  /**
   * 上游**最新版**原文的發布日（ISO）；讀不到時為 null。
   *
   * ⚠️ **刻意不用於任何顯示**（2026-09-08 查證確認）。站上所有日期都取
   * `current.date`（= `br-versions.ts` 的人工記錄）。升版期間 BR.md 已換成新版原文，
   * 此欄位會是**新版**的日期，若拿來標示本站發布版，就會出現「v2.2.7 · 2026-08-06」
   * 這種張冠李戴。同 `version` 欄位的鐵則：上游的值只能用來判斷是否落後、以及顯示
   * 「上游 vX.Y.Z」，絕不可當成本站的值。
   *
   * 目前唯一的用途是保留給日後的落後提示（如「上游已於 X 日發布新版」）。
   */
  date: string | null;
}

/** 讀 web-spec-doc/BR.md 的 front-matter，取得上游最新版與日期。 */
function readUpstream(): UpstreamInfo {
  const head = brMdRaw.slice(0, 2048);
  const version = /^subtitle:\s*Version\s+(\S+)\s*$/m.exec(head)?.[1] ?? null;
  const rawDate = /^date:\s*(\S+)\s*$/m.exec(head)?.[1] ?? null;
  return { version, date: rawDate ? parseBrDate(rawDate) : null };
}

export const upstream: UpstreamInfo = readUpstream();

/** 本站目前發布的版本（brVersions 最上面那列）。 */
export const current: BrVersionEntry = brVersions[0];

/** 本站是否落後上游（兩邊版本號不同即視為落後）。 */
export const isBehind: boolean = upstream.version !== null && upstream.version !== current.version;

/** 徽章與頁面共用的顯示字串。 */
export const versionLabel = `v${current.version}`;
export const versionDate = current.date;
