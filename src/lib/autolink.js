// Автолінковка індексів документів у тексті (ядро продукту).
// Працює на етапі збірки: текст -> безпечний HTML з <a class="doclink">.

const IDX_RE = /(?<![А-ЯІЇЄҐа-яіїєґA-Za-z0-9-])(Б[1-3]|В[1-7]|Г[1-9]|Д[1-5]|Е[1-9])(?![0-9А-ЯІЇЄҐа-яіїєґA-Za-z-])/g;
const DOD_A_RE = /(Додаток А|Дод\. А)(?![0-9А-ЯІЇЄҐа-яіїєґ])/g;

const esc = (s) => s
  .replaceAll('&', '&amp;').replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;').replaceAll('"', '&quot;');

function translit(idx) {
  const map = { 'А': 'a', 'Б': 'b', 'В': 'v', 'Г': 'g', 'Д': 'd', 'Е': 'e' };
  return map[idx[0]] + idx.slice(1);
}

/**
 * @param {string} text  сирий текст
 * @param {object} opts  { base, lang, dict, selfIndex, terms }
 */
export function autolink(text, { base, lang, dict, selfIndex = null, terms = {} } = {}) {
  let html = esc(text);
  const href = (slug) => `${base}${lang}/docs/${slug}/`;

  html = html.replace(IDX_RE, (m) => {
    if (m === selfIndex || !dict[m]) return m;
    return `<a class="doclink" href="${href(translit(m))}" title="${esc(dict[m].name)}">${m}</a>`;
  });
  html = html.replace(DOD_A_RE, (m) => {
    if (selfIndex === 'А') return m;
    return `<a class="doclink" href="${href('a')}" title="${esc(dict['А']?.name ?? 'Календар звітності')}">${m}</a>`;
  });
  for (const [term, slug] of Object.entries(terms)) {
    const re = new RegExp(`(?<![А-ЯІЇЄҐа-яіїєґ])(${term[0].toUpperCase()}|${term[0]})${term.slice(1)}`, 'g');
    const selfSlug = selfIndex ? translit(selfIndex) : null;
    if (slug === selfSlug) continue;
    html = html.replace(re, (m) => `<a class="doclink" href="${href(slug)}">${m}</a>`);
  }
  return html;
}
