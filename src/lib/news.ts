// 更新消息（news collection）的共用工具：排序、日期字串、分類徽章配色。
// 首頁（src/pages/index.astro）、列表頁與詳細頁三處共用，避免各寫一份而走樣。
import type { CollectionEntry } from 'astro:content';

export type NewsEntry = CollectionEntry<'news'>;

/** 由新到舊；同日再以 slug 排序，確保每次 build 的順序一致。 */
export function sortNews(entries: NewsEntry[]): NewsEntry[] {
  return [...entries].sort(
    (a, b) =>
      b.data.date.getTime() - a.data.date.getTime() ||
      a.data.slug.localeCompare(b.data.slug),
  );
}

/** YYYY-MM-DD；畫面顯示與 <time datetime> 共用同一個字串。 */
export function toIsoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

// 分類徽章配色。分類值由 content.config.ts 的 z.enum 限定，新增分類要同時補這裡。
const CATEGORY_CLASS: Record<string, string> = {
  站務公告: 'border-slate-300 bg-slate-100 text-slate-700',
  翻譯更新: 'border-bs-primary bg-bs-primary-soft text-bs-secondary',
  原文動態: 'border-amber-300 bg-amber-50 text-amber-800',
  勘誤: 'border-rose-300 bg-rose-50 text-rose-800',
};

export function newsCategoryClass(category: string): string {
  return CATEGORY_CLASS[category] ?? CATEGORY_CLASS['站務公告'];
}
