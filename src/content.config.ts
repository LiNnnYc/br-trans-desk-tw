import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// spec §3.1 — BR 章節細項
const br = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/br' }),
  schema: z.object({
    title: z.string().min(1),
    section_id: z
      .string()
      .regex(
        /^(\d+(\.\d+)*|appendix-[a-z])$/,
        'section_id 須為點分數字（如 "3.2.2.4"）或附錄識別碼（如 "appendix-a"）',
      ),
    parent: z
      .string()
      .regex(/^(\d+(\.\d+)*|appendix-[a-z])$/)
      .optional(),
    order: z.number().int().nonnegative(),
    original_url: z.string().url(),
    original_version: z.string().min(1),
    ballot_refs: z.array(z.string()).default([]),
    translator: z.string().min(1),
    last_updated: z.coerce.date(),
    status: z.enum(['draft', 'translated', 'reviewed', 'outdated']),
    tags: z.array(z.string()).default([]),
  }),
});

// spec §3.2 — 術語表（多來源一字多義；見 memory project_glossary_multisource）
// 一個英文詞一個檔，sources[] 裝多來源譯名/定義；recommended_zh 為總覽頁顯示的推薦譯名。
const glossarySource = z.object({
  /** 來源代碼：BR｜HiPKICA｜TWCA｜（未來）NCSSR / Root Program 等 */
  source: z.string().min(1),
  term_zh: z.string().min(1),
  definition: z.string().min(1),
  /** 站內路徑（/server-cert-br/...）或外部文件引用字串（如「HiPKICA CP/CPS v1.1 附錄 2」） */
  ref: z.string().optional(),
});

const glossary = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/glossary' }),
  schema: z.object({
    term_en: z.string().min(1),
    abbreviation: z.string().optional(),
    /** 推薦譯名（總覽頁顯示）；BR 有的詞預設＝§1.6.1/§1.6.2 定版 */
    recommended_zh: z.string().min(1),
    /** 推薦譯名採自哪個來源 */
    recommended_source: z.string().optional(),
    /** 各來源的譯名與定義；至少一筆 */
    sources: z.array(glossarySource).min(1),
    // 此詞在 BR 章節細項首次出現的頁面路徑（若已知）
    first_seen_at: z
      .string()
      .regex(/^\/server-cert-br\/.+\/$/, 'first_seen_at 須為 /server-cert-br/ 下的頁面路徑')
      .optional(),
    tags: z.array(z.string()).default([]),
  }),
});

// spec §3.3 — 客服爭議卡片
const quickReference = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/quick-reference' }),
  schema: z.object({
    slug: z.string().regex(/^[a-z0-9-]+$/, 'slug 須為小寫英數與連字號'),
    question: z.string().min(1),
    short_answer: z.string().min(1),
    related_sections: z
      .array(z.string().regex(/^\d+(\.\d+)*$/))
      .min(1, '至少需關聯一節 BR 章節細項'),
    last_updated: z.coerce.date(),
  }),
});

export const collections = {
  br,
  glossary,
  'quick-reference': quickReference,
};
