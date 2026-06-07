// 全站共用設定。spec §4.1 版本徽章、§9.1 頁尾聲明所需資訊集中於此。

export type SyncStatus = 'synced' | 'behind' | 'pending';

export const siteConfig = {
  name: 'CA/Browser BRs 與瀏覽器 Root Program Policy 的翻譯小站',
  shortName: 'BR 翻譯小站',
  description:
    'CA/Browser Forum Baseline Requirements 和各瀏覽器 Root Program Policy 的非官方繁體中文翻譯',
  // M0-1 建立 GitHub repo 後替換
  repoUrl: '#TODO-github-repo',
  // 引用卡輸出絕對網址用；M0-3 部署網域定案時更新（含或不含 /repo-name 由 astro.config base 決定）
  siteUrl: 'https://br-zh-tw.github.io',
  contactEmail: 'linnnyc5252@gmail.com',
  // spec §4.1 版本徽章資料來源。M2 啟動翻譯時填入實際值。
  // CI 後續可寫腳本覆寫此區塊（例如 Ballot 跟進完成後 bump version + behindCount）。
  upstream: {
    version: 'tbd' as string,
    // ISO yyyy-mm-dd；null 表示尚未同步
    lastSyncedAt: null as string | null,
    syncStatus: 'pending' as SyncStatus,
    behindCount: 0,
  },
} as const;
