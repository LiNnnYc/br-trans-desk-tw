// remark-fancy-lists：補上 CommonMark 不支援的「字母 / 羅馬數字」清單。
//
// 上游 BR.md（Pandoc 風格）以 `a.` / `b.`、`i.` / `ii.` / `iii.` 等標記表示
// 巢狀清單；cabforum.org 經 Pandoc 會渲染成 <ol type="a"> / <ol type="i">。
// Astro 的 remark/CommonMark 流程不認得這類標記，於是它們被當成段落純文字
// （不縮排、不成清單）。此 plugin 在 mdast 階段把這些標記行重建為帶
// `type` 屬性的 <ol>，使排版對齊 cabforum.org。
//
// 偵測限制（保守，避免誤判一般散文）：
//   - 標記必須位於某個 paragraph 內、以 softbreak 分隔的「行首」。
//   - 標記為單一小寫字母（a-z）或羅馬數字字元組（i/ii/iii/iv…）後接 `. ` 。
//   - 巢狀關係由標記類型推斷：字母為上層時，其後的羅馬數字視為其子層
//     （本文件最深僅兩層，符合 BR 全文實際結構）。
//
// 處理的兩種來源結構：
//   1. 單一段落內含「前導行 + 標記行」（例：編號清單項目 "遵守\n   a. …\n   b. …"，
//      或 "CA 在簽發時：\n   i. …\n   ii. …"）。
//   2. 連續的兄弟段落各自以標記行開頭（例 §3.2.2.3 的 a./b./c./d. 各自成段，
//      其中 a. 段內又夾帶 i./ii. 子項）。

const ROMAN_RE = /^[ivxlcdm]+$/;

/** 判定標記字串屬於字母清單還是羅馬數字清單；非法標記回傳 null。 */
function classify(marker) {
  if (ROMAN_RE.test(marker)) {
    // 多字元（ii, iii, iv…）或單一 'i' 視為羅馬數字；
    // 其餘單一字元（c, d, v, x…）在本語料中只會是字母清單。
    if (marker.length > 1 || marker === 'i') return 'roman';
    return 'alpha';
  }
  if (marker.length === 1) return 'alpha';
  return null;
}

const ROMAN_VALUES = { i: 1, v: 5, x: 10, l: 50, c: 100, d: 500, m: 1000 };
function romanToInt(s) {
  let total = 0;
  for (let i = 0; i < s.length; i++) {
    const cur = ROMAN_VALUES[s[i]];
    const next = ROMAN_VALUES[s[i + 1]];
    total += next && cur < next ? -cur : cur;
  }
  return total;
}
function markerToInt(marker, type) {
  return type === 'roman' ? romanToInt(marker) : marker.charCodeAt(0) - 96;
}

/**
 * 把 paragraph 的 inline children 依 softbreak（text 內的 \n）與 hard break
 * 切成多「行」，每行是 inline node 陣列。
 */
function splitLines(children) {
  const lines = [[]];
  for (const child of children) {
    if (child.type === 'text' && child.value.includes('\n')) {
      const parts = child.value.split('\n');
      parts.forEach((part, idx) => {
        if (idx > 0) lines.push([]);
        if (part !== '') lines[lines.length - 1].push({ type: 'text', value: part });
      });
    } else if (child.type === 'break') {
      lines.push([]);
    } else {
      lines[lines.length - 1].push(child);
    }
  }
  return lines;
}

/** 取得某行的清單標記（若該行以合法標記開頭），否則 null。 */
function lineMarker(line) {
  if (line.length === 0) return null;
  const first = line[0];
  if (first.type !== 'text') return null;
  const m = /^([a-z]+)\.[ \t]+/.exec(first.value);
  if (!m) return null;
  const type = classify(m[1]);
  if (!type) return null;
  return { marker: m[1], type, raw: m[0] };
}

/** 移除某行開頭的標記，回傳乾淨的 inline node 陣列（保留後續 link/strong 等）。 */
function stripMarker(line, raw) {
  const out = line.slice();
  const first = { ...out[0] };
  first.value = first.value.slice(raw.length);
  out[0] = first;
  return out;
}

/** 建立帶 hProperties type 的 ordered list 節點。 */
function makeList(type, startNum) {
  const list = {
    type: 'list',
    ordered: true,
    spread: false,
    children: [],
    data: { hName: 'ol', hProperties: { type: type === 'roman' ? 'i' : 'a' } },
  };
  if (startNum && startNum !== 1) list.data.hProperties.start = startNum;
  return list;
}

function makeItem(inlineNodes) {
  return {
    type: 'listItem',
    spread: false,
    children: [{ type: 'paragraph', children: inlineNodes }],
  };
}

/**
 * 把「標記行串流」建成最多兩層的巢狀 ol。
 * 第一個標記決定上層類型；不同類型的後續標記巢狀於目前的上層項目下。
 */
function buildList(markerLines) {
  const topType = markerLines[0].mark.type;
  const root = makeList(topType, markerToInt(markerLines[0].mark.marker, topType));
  let lastTopItem = null;
  let subList = null;

  for (const { line, mark } of markerLines) {
    const item = makeItem(stripMarker(line, mark.raw));
    if (mark.type === topType) {
      root.children.push(item);
      lastTopItem = item;
      subList = null;
    } else {
      // 子層（例：字母上層下的羅馬數字）
      if (!subList) {
        subList = makeList(mark.type, markerToInt(mark.marker, mark.type));
        (lastTopItem ?? makeItemFallback(root)).children.push(subList);
      }
      subList.children.push(item);
    }
  }
  return root;
}

// 極端防呆：子層出現但尚無上層項目時，補一個空上層項目掛載（理論上 BR 不會發生）。
function makeItemFallback(root) {
  const item = makeItem([{ type: 'text', value: '' }]);
  root.children.push(item);
  return item;
}

/** 由「前導行 + 標記行」的 line 陣列產生 [前導 paragraph?, ol] 節點。 */
function buildFromLines(lines) {
  const annotated = lines.map((line) => ({ line, mark: lineMarker(line) }));
  const firstMarkerIdx = annotated.findIndex((a) => a.mark);
  const leadLines = annotated.slice(0, firstMarkerIdx).map((a) => a.line);
  const markerLines = annotated.slice(firstMarkerIdx);

  const result = [];
  if (leadLines.length) {
    const leadNodes = [];
    leadLines.forEach((line, idx) => {
      if (idx > 0) leadNodes.push({ type: 'text', value: ' ' });
      leadNodes.push(...line);
    });
    if (leadNodes.length) result.push({ type: 'paragraph', children: leadNodes });
  }
  result.push(buildList(markerLines));
  return result;
}

/** 段落是否含任一標記行。 */
function paragraphHasMarker(node) {
  if (node.type !== 'paragraph') return false;
  return splitLines(node.children).some((line) => lineMarker(line));
}

/** 段落「首行」是否為標記行（用於判斷兄弟段落是否延續同一清單）。 */
function paragraphStartsWithMarker(node) {
  if (node.type !== 'paragraph') return false;
  const lines = splitLines(node.children);
  return lines.length > 0 && !!lineMarker(lines[0]);
}

function transform(parent) {
  if (!parent.children) return;
  const newChildren = [];
  let i = 0;
  while (i < parent.children.length) {
    const node = parent.children[i];
    if (paragraphHasMarker(node)) {
      let lines = splitLines(node.children);
      // 合併後續「以標記行開頭」的兄弟段落（§3.2.2.3 的 a./b./c./d. 各自成段）
      let j = i + 1;
      while (j < parent.children.length && paragraphStartsWithMarker(parent.children[j])) {
        lines = lines.concat(splitLines(parent.children[j].children));
        j++;
      }
      newChildren.push(...buildFromLines(lines));
      i = j;
      continue;
    }
    transform(node);
    newChildren.push(node);
    i++;
  }
  parent.children = newChildren;
}

export function remarkFancyLists() {
  return (tree) => {
    transform(tree);
  };
}
