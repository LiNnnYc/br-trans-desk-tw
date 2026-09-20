// 用戶憑證最長有效期的階段表（SC-081 排程）。
//
// **唯一資料來源是 BR §6.3.2**（src/content/br/6-3-2.md 的參考表格），本檔是它的機器可讀版本，
// 供首頁側欄的 ValidityWidget 使用。上游若再調整排程，**先改 §6.3.2 的譯文，再回來同步本檔**。
//
// 兩個數字的差別（§6.3.2 原文）：
//   maxDays         不得（MUST NOT）超過 —— 規範上限
//   recommendedDays 不宜（SHOULD NOT）超過 —— 實務上 CA 多以此簽發，
//                   因為 1 日以 86,400 秒計，多出零點幾秒就算多一日，簽到上限容易踩線
//
// `from`／`to` 為 ISO 日期字串，半開區間 [from, to)；`null` 表示沒有該側邊界。

export interface ValidityStage {
  from: string | null;
  to: string | null;
  maxDays: number;
  recommendedDays: number;
}

export const validityStages: ValidityStage[] = [
  { from: null, to: '2026-03-15', maxDays: 398, recommendedDays: 397 },
  { from: '2026-03-15', to: '2027-03-15', maxDays: 200, recommendedDays: 199 },
  { from: '2027-03-15', to: '2029-03-15', maxDays: 100, recommendedDays: 99 },
  { from: '2029-03-15', to: null, maxDays: 47, recommendedDays: 46 },
];

/** 依日期（ISO yyyy-mm-dd）取當下適用的階段索引；找不到時回傳最後一段。 */
export function stageIndexOn(isoDate: string): number {
  const i = validityStages.findIndex(
    (s) => (s.from === null || isoDate >= s.from) && (s.to === null || isoDate < s.to),
  );
  return i === -1 ? validityStages.length - 1 : i;
}

/** 本表的規範出處（widget 顯示用） */
export const validitySourceSection = '6.3.2';
