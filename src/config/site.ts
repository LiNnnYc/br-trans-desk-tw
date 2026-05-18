// 全站共用設定。spec §4.1 版本徽章、§9.1 頁尾聲明所需資訊集中於此。

export type SyncStatus = 'synced' | 'behind' | 'pending';

export const siteConfig = {
  name: 'CA/Browser BR 翻譯',
  shortName: 'BR 翻譯',
  description:
    'CA/Browser Forum Server Certificate Baseline Requirements 的非官方繁體中文翻譯。',
  // M0-1 建立 GitHub repo 後替換
  repoUrl: '#TODO-github-repo',
  contactEmail: 'linnnyc5252@gmail.com',
  // spec §4.1 版本徽章資料來源。M2 啟動翻譯時填入實際值。
  upstream: {
    version: 'tbd' as string,
    lastSyncedAt: null as string | null,
    syncStatus: 'pending' as SyncStatus,
    behindCount: 0,
  },
} as const;
