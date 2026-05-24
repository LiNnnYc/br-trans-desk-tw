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

// spec §3.2 — 術語表
const glossary = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/glossary' }),
  schema: z.object({
    term_en: z.string().min(1),
    term_zh: z.string().min(1),
    abbreviation: z.string().optional(),
    definition: z.string().min(1),
    // first_seen_at 在 BR 章節細項未建立前可以缺漏；M2 翻譯過程會逐步補上
    first_seen_at: z
      .string()
      .regex(/^\/server-cert-br\/.+\/$/, 'first_seen_at 須為 /server-cert-br/ 下的頁面路徑')
      .optional(),
    /** 譯名來源；目前主要為 HiPKICA CP/CPS 附錄 1/2 */
    source: z.string().optional(),
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
