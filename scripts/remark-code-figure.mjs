/**
 * Remark plugin that wraps each fenced code block in a <figure> with a
 * toolbar (language label + copy button). The language is captured at the
 * mdast layer, BEFORE Astro/Shiki rewrites unknown languages to "plaintext".
 *
 * Run by Astro via astro.config.mjs > markdown.remarkPlugins.
 *
 * Why a remark plugin (not a Shiki transformer):
 *   By the time Shiki's transformer hooks fire, Astro has already replaced
 *   unknown fence labels (ASN.1, hexdump, DNSZone …) with "plaintext", so
 *   the original label is unrecoverable from the transformer side.
 */
import { visit } from 'unist-util-visit';

function escapeHtml(s) {
  return String(s)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

export function remarkCodeFigure() {
  return (tree) => {
    const targets = [];
    visit(tree, 'code', (node, idx, parent) => {
      if (!parent || idx == null) return;
      targets.push({ parent, idx, lang: node.lang || 'code' });
    });
    // Insert in reverse to keep earlier indices stable.
    for (const { parent, idx, lang } of targets.sort((a, b) => b.idx - a.idx)) {
      const opener = {
        type: 'html',
        value:
          `<figure class="code-figure">` +
          `<figcaption class="code-figure-header">` +
          `<span class="code-figure-lang">${escapeHtml(lang)}</span>` +
          `<button type="button" class="code-figure-copy" aria-label="複製程式碼" data-copy-state="idle">複製</button>` +
          `</figcaption>`,
      };
      const closer = { type: 'html', value: `</figure>` };
      parent.children.splice(idx + 1, 0, closer);
      parent.children.splice(idx, 0, opener);
    }
  };
}

export default remarkCodeFigure;
