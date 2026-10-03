// 全站共用設定。spec §4.1 版本徽章、§9.1 頁尾聲明所需資訊集中於此。
import { current, isBehind, upstream as upstreamLatest } from '../lib/version';

export type SyncStatus = 'synced' | 'behind' | 'pending';

export const siteConfig = {
  name: 'BR 翻譯小站',
  shortName: 'BR 小站',
  description:
    'WebPKI 相關文件的非官方繁體中文翻譯',
  repoUrl: 'https://github.com/LiNnnYc/br-trans-desk-tw',
  // 結構化資料（schema.org）等絕對網址用；須與 astro.config.mjs 的 site 一致
  siteUrl: 'https://tls.brdesk.tw',
  contactEmail: 'tls@brdesk.tw',
  // spec §6.3 GoatCounter 站台代碼（https://<code>.goatcounter.com）。空字串＝不載入統計 script；
  // 只在 production build 載入（見 BaseLayout），本機 dev 不計數。
  goatcounterCode: 'brdesk',
  // spec §4.1 版本徽章資料來源。**不再手動維護**——由 src/lib/version.ts 推導：
  //   version      = 本站發布版（src/config/br-versions.ts 的 brVersions[0]）
  //   lastSyncedAt = 該版原文發布日（取自當時 BR.md 標頭的 date）
  //   syncStatus   = 與 upstream/BR.md 標頭的上游版本比對
  // 升版只需在 br-versions.ts 加一列，全站顯示自動跟著更新。
  upstream: {
    version: current.version,
    /** 本站發布版的**原文發布日**（ISO yyyy-mm-dd） */
    lastSyncedAt: current.date as string | null,
    syncStatus: (isBehind ? 'behind' : 'synced') as SyncStatus,
    /** 上游最新版本號；未落後時與 version 相同 */
    upstreamVersion: upstreamLatest.version,
    behindCount: 0,
  },
} as const;
