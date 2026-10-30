// Генератор трьох варіантів головної в стилі Apple (примірка перед редизайном).
// Дані беруться з реальних src/i18n/uk.json і src/data/uk/roles.json.
import fs from 'node:fs';
const U = JSON.parse(fs.readFileSync(new URL('../../src/i18n/uk.json', import.meta.url)));
const R = JSON.parse(fs.readFileSync(new URL('../../src/data/uk/roles.json', import.meta.url)));
const roles = Array.isArray(R) ? R : (R.roles || Object.values(R));
const H = U.home, N = U.nav;
const ORDER = ['nachalnyk-dilnytsi', 'prorab', 'vtv', 'kp', 'tehnahliad', 'koshtorysnyk', 'ksz', 'zakupivli'];
const main = ORDER.map((s) => roles.find((r) => r.slug === s)).filter(Boolean);
const cap = (s) => String(s).charAt(0).toUpperCase() + String(s).slice(1);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const dash = (s) => esc(s);

const I = {
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  users: '<circle cx="9" cy="8" r="3.5"/><path d="M3.5 20c.5-3.5 2.8-5 5.5-5s5 1.5 5.5 5"/><circle cx="17" cy="9" r="2.5"/><path d="M16.5 14.5c2.3.2 3.7 1.6 4 4.5"/>',
  doc: '<path d="M14 3v5h5M7 3h7l5 5v13H7z"/><path d="M10 12h5M10 16h5"/>',
  route: '<circle cx="6" cy="19" r="2.5"/><circle cx="18" cy="5" r="2.5"/><path d="M8.5 19H15a3.5 3.5 0 0 0 0-7H9a3.5 3.5 0 0 1 0-7h6.5"/>',
  cal: '<rect x="4" y="5" width="16" height="16" rx="2.5"/><path d="M4 10h16M9 3v4M15 3v4"/>',
  check: '<path d="M9 11l3 3 8-8"/><path d="M20 12v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h9"/>',
  book: '<path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3zM19 17H8a3 3 0 0 0 0 6h11"/>',
  coins: '<circle cx="9" cy="9" r="6"/><path d="M9 6.5v5M7 8h4M16 8a6 6 0 1 1-7.7 7.7"/>',
  mega: '<path d="M4 10v4a1 1 0 0 0 1 1h2l4 4V5L7 9H5a1 1 0 0 0-1 1z"/><path d="M14 9a4 4 0 0 1 0 6M17 7a7.5 7.5 0 0 1 0 10"/>',
  chev: '<path d="m9 6 6 6-6 6"/>',
  left: '<path d="m15 6-6 6 6 6"/>',
};
const ico = (n, s = 20, w = 1.8) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${I[n]}</svg>`;

const SECTIONS = [
  { k: 'roles', ico: 'users', label: N.roles, sub: '14 ролей', tint: '#0071e3' },
  { k: 'docs', ico: 'doc', label: N.docs, sub: '34 документи', tint: '#34a853' },
  { k: 'processes', ico: 'route', label: N.processes, sub: '5 схем', tint: '#ff9500' },
  { k: 'calendar', ico: 'cal', label: N.calendar, sub: 'хто, що і коли', tint: '#ff3b30' },
  { k: 'checklists', ico: 'check', label: N.checklists, sub: '6 списків', tint: '#5856d6' },
  { k: 'kernel', ico: 'book', label: N.kernel, sub: '5 розділів', tint: '#8e8e93' },
];

const BASE = `
:root{
  --bg:#fff; --bg2:#f5f5f7; --ink:#1d1d1f; --ink2:#6e6e73; --ink3:#86868b; --line:rgba(0,0,0,.08);
  --link:#0066cc; --accent:#0071e3; --gold:#b8963f;
  --sans:-apple-system,BlinkMacSystemFont,"SF Pro Text","Inter","Segoe UI",Roboto,sans-serif;
  --display:-apple-system,BlinkMacSystemFont,"SF Pro Display","Inter","Segoe UI",Roboto,sans-serif;
  --ease:cubic-bezier(.25,.1,.25,1);
}
*{box-sizing:border-box} html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.47 var(--sans);letter-spacing:-.022em;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:1024px;margin:0 auto;padding:0 22px}
.link{color:var(--link)} .link:hover{text-decoration:underline}
/* translucent global nav */
.gnav{position:sticky;top:0;z-index:50;height:48px;background:rgba(251,251,253,.8);backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);border-bottom:1px solid var(--line)}
.gnav .in{max-width:1024px;margin:0 auto;padding:0 22px;height:100%;display:flex;align-items:center;gap:28px}
.gnav .logo{display:flex;align-items:center;gap:9px;font:600 14px/1 var(--sans);letter-spacing:-.01em}
.gnav .logo img{height:22px}
.gnav nav{display:flex;gap:26px;margin:0 auto;font-size:12.5px;letter-spacing:-.01em;color:rgba(0,0,0,.8)}
.gnav nav a:hover{color:#000}
.gnav .tools{display:flex;align-items:center;gap:18px;font-size:12px;color:rgba(0,0,0,.8)}
.gnav .lang b{font-weight:600}
.btn{display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:0 22px;border-radius:980px;background:var(--accent);color:#fff;font:400 17px/1 var(--sans);transition:background .2s var(--ease),transform .1s ease-out}
.btn:hover{background:#0077ed} .btn:active{transform:scale(.97)}
.btn.ghost{background:none;color:var(--link);border:1px solid var(--link)}
.press{transition:transform .25s var(--ease),box-shadow .25s var(--ease)} .press:active{transform:scale(.98)}
.foot{border-top:1px solid var(--line);background:var(--bg2);color:var(--ink3);font-size:12px;letter-spacing:-.01em;padding:18px 0 28px}
.foot .wrap{display:flex;gap:16px;flex-wrap:wrap;justify-content:space-between}
@media (max-width:833px){ .gnav nav{display:none} .gnav .in{justify-content:space-between} }
@media (prefers-reduced-motion:reduce){ *{transition:none!important;animation:none!important} }
@media (prefers-reduced-transparency:reduce){ .gnav{background:#fbfbfd;backdrop-filter:none} }
`;

const gnav = () => `<header class="gnav"><div class="in">
  <a class="logo" href="#"><img src="img/dobrograd-mark.svg" alt="">ОС будблоку</a>
  <nav>${SECTIONS.map((s) => `<a href="#">${esc(s.label)}</a>`).join('')}</nav>
  <div class="tools"><a href="#" aria-label="Пошук">${ico('search', 16, 1.7)}</a><span class="lang"><b>УКР</b> · РУС · ENG</span></div>
</div></header>`;
const foot = () => `<footer class="foot"><div class="wrap"><span>Iron Invest · Доброград. Внутрішня база знань будівельного блоку.</span><span>${esc(U.site.motto)}</span></div></footer>`;
const page = (title, css, body) => `<!doctype html><html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400..700&display=swap" rel="stylesheet">
<style>${BASE}${css}</style></head><body>${body}</body></html>`;

/* ===================== A · apple.com ===================== */
const A = page('A · Вітрина', `
.hero{text-align:center;padding-block:96px 72px}
.eyebrow{font:600 17px/1.2 var(--sans);color:var(--gold);letter-spacing:-.01em}
.hero h1{margin:10px auto 0;max-width:820px;font:600 clamp(40px,6.4vw,72px)/1.05 var(--display);letter-spacing:-.035em}
.hero p{margin:18px auto 0;max-width:640px;font-size:21px;line-height:1.38;color:var(--ink2);letter-spacing:-.016em}
.sbox{margin:36px auto 0;max-width:600px;display:flex;align-items:center;gap:12px;height:56px;padding:0 20px;border-radius:16px;background:var(--bg2);color:var(--ink3);font-size:17px;text-align:left;transition:background .2s var(--ease)}
.sbox:hover{background:#ebebef}
.quick{margin-top:20px;display:flex;gap:26px;justify-content:center;flex-wrap:wrap;font-size:15px}
.quick a{color:var(--link)} .quick a:hover{text-decoration:underline}
.band{background:var(--bg2);padding:80px 0 88px}
.h2{font:600 clamp(32px,4.2vw,48px)/1.08 var(--display);letter-spacing:-.03em;margin:0}
.h2 + p{margin:10px 0 0;font-size:19px;color:var(--ink2)}
.gal{margin-top:40px;display:flex;gap:20px;overflow-x:auto;scroll-snap-type:x mandatory;--gp:max(22px,calc((100vw - 1024px)/2 + 22px));padding:4px var(--gp) 24px;scroll-padding-inline:var(--gp);scrollbar-width:none}
.gal::-webkit-scrollbar{display:none}
.rc{flex:0 0 300px;scroll-snap-align:start;background:#fff;border-radius:28px;padding:30px 28px 28px;display:flex;flex-direction:column;min-height:440px;box-shadow:0 2px 12px rgba(0,0,0,.04)}
.rc:hover{box-shadow:0 10px 40px rgba(0,0,0,.08);transform:scale(1.012)}
.rc .k{font:600 12px/1 var(--sans);letter-spacing:.02em;color:var(--ink3);text-transform:uppercase}
.rc h3{margin:10px 0 0;font:600 26px/1.12 var(--display);letter-spacing:-.025em}
.rc p{margin:10px 0 0;font-size:15px;line-height:1.42;color:var(--ink2)}
.rc img{margin-top:auto;width:100%;height:190px;object-fit:contain}
.gal-nav{display:flex;justify-content:flex-end;gap:14px;margin-top:4px}
.gal-nav button{width:36px;height:36px;border-radius:50%;border:0;background:#e3e3e8;color:var(--ink);display:grid;place-items:center;cursor:pointer}
.bento{padding-block:88px}
.grid{margin-top:40px;display:grid;grid-template-columns:repeat(6,1fr);gap:20px}
.tile{background:var(--bg2);border-radius:28px;padding:32px;min-height:240px;display:flex;flex-direction:column;justify-content:space-between}
.tile .n{font:600 72px/1 var(--display);letter-spacing:-.04em}
.tile h3{margin:0;font:600 24px/1.15 var(--display);letter-spacing:-.022em}
.tile p{margin:6px 0 0;color:var(--ink2);font-size:15px}
.tile .go{color:var(--link);font-size:15px;margin-top:14px}
.t1{grid-column:span 3}.t2{grid-column:span 3}.t3{grid-column:span 2}.t4{grid-column:span 2}.t5{grid-column:span 2}
.t1{background:#1d1d1f;color:#f5f5f7}.t1 p{color:#a1a1a6}.t1 .go{color:#2997ff}
.motto{padding:110px 0 120px;text-align:center}
.motto q{display:block;max-width:820px;margin:0 auto;font:600 clamp(30px,4.4vw,52px)/1.1 var(--display);letter-spacing:-.03em;quotes:none}
.motto span{display:block;margin-top:16px;color:var(--ink2);font-size:17px}
@media (max-width:833px){.grid{grid-template-columns:1fr}.t1,.t2,.t3,.t4,.t5{grid-column:auto}.hero{padding-block:64px 48px}.tile{min-height:180px}.rc{flex-basis:78vw}}
`, `${gnav()}
<main>
<section class="hero wrap">
  <div class="eyebrow">Iron Invest · Доброград</div>
  <h1>Регламенти будівельного блоку. В одному місці.</h1>
  <p>${dash(H.heroLead)}</p>
  <a class="sbox press" href="#">${ico('search', 19)}<span>${esc(H.searchTitle)}</span></a>
  <div class="quick">${H.quickQueries.map((q) => `<a href="#">${esc(q.label)} ›</a>`).join('')}</div>
</section>
<section class="band">
  <div class="wrap"><h2 class="h2">Оберіть свою роль.</h2><p>${dash(H.rolesHint)}</p></div>
  <div class="gal">${main.map((r) => `<a class="rc press" href="#"><span class="k">${esc(r.group || 'Роль')}</span><h3>${esc(r.title)}</h3><p>${dash(cap(r.short))}</p><img src="img/role-${r.slug}.webp" alt=""></a>`).join('')}</div>
  <div class="wrap gal-nav"><button aria-label="Назад">${ico('left', 18, 2.2)}</button><button aria-label="Далі">${ico('chev', 18, 2.2)}</button></div>
</section>
<section class="bento wrap">
  <h2 class="h2">Усе для щоденної роботи.</h2><p>Документи, процеси, строки і перевірки. Відкривається з телефона на майданчику.</p>
  <div class="grid">
    <a class="tile t1 press" href="#"><div><div class="n">34</div></div><div><h3>Документи і форми</h3><p>Реєстр з посиланнями на Диск і датами оновлення.</p><div class="go">Відкрити реєстр ›</div></div></a>
    <a class="tile t2 press" href="#"><div><div class="n">8</div></div><div><h3>Шлях платежу</h3><p>Кроків від ініціації до оплати.</p><div class="go">Пройти шлях ›</div></div></a>
    <a class="tile t3 press" href="#"><div><div class="n">5</div></div><div><h3>Процеси</h3><p>Покрокові схеми.</p></div></a>
    <a class="tile t4 press" href="#"><div><div class="n">6</div></div><div><h3>Чек-листи</h3><p>З галочками і прогресом.</p></div></a>
    <a class="tile t5 press" href="#"><div><div class="n">25</div></div><div><h3>Календар</h3><p>План до 25, звіт до 5.</p></div></a>
  </div>
</section>
<section class="motto"><q>${esc(U.site.motto)}</q><span>Головне правило служби замовника.</span></section>
</main>${foot()}`);

/* ===================== B · Settings / Docs ===================== */
const B = page('B · Довідник', `
body{background:#f2f2f7}
.shell{display:grid;grid-template-columns:268px 1fr;min-height:100vh}
.side{position:sticky;top:0;height:100vh;overflow:auto;padding:18px 12px;background:rgba(246,246,248,.72);backdrop-filter:saturate(180%) blur(30px);-webkit-backdrop-filter:saturate(180%) blur(30px);border-right:1px solid var(--line)}
.side .logo{display:flex;align-items:center;gap:10px;padding:6px 10px 16px;font:600 15px/1.2 var(--sans)}
.side .logo img{height:26px}
.side .logo small{display:block;font-weight:400;color:var(--ink3);font-size:12px}
.side .s{display:flex;align-items:center;gap:8px;height:34px;margin:0 4px 14px;padding:0 10px;border-radius:9px;background:rgba(118,118,128,.12);color:var(--ink3);font-size:14px}
.side h6{margin:16px 12px 6px;font:600 11px/1 var(--sans);letter-spacing:.02em;color:var(--ink3);text-transform:uppercase}
.side a.it{display:flex;align-items:center;gap:10px;height:34px;padding:0 8px;border-radius:8px;font-size:14px;letter-spacing:-.01em}
.side a.it:hover{background:rgba(0,0,0,.04)} .side a.it.on{background:rgba(0,0,0,.07);font-weight:500}
.sq{width:24px;height:24px;border-radius:6px;display:grid;place-items:center;color:#fff;flex:none}
.content{padding:56px 48px 80px;max-width:860px}
.lt{font:700 40px/1.1 var(--display);letter-spacing:-.03em;margin:0}
.lead{margin:10px 0 0;color:var(--ink2);font-size:19px;max-width:640px}
.sb{margin-top:26px;display:flex;align-items:center;gap:10px;height:44px;padding:0 14px;border-radius:12px;background:rgba(118,118,128,.12);color:var(--ink3);font-size:17px;max-width:560px}
.gh{margin:40px 16px 8px;font:400 13px/1 var(--sans);color:var(--ink2);text-transform:uppercase;letter-spacing:-.01em}
.grp{background:#fff;border-radius:14px;overflow:hidden}
.row{display:flex;align-items:center;gap:14px;min-height:60px;padding:10px 16px;position:relative;transition:background .15s ease}
.row:hover{background:#f7f7f9} .row:active{background:#ececf0}
.row + .row::before{content:"";position:absolute;top:0;left:60px;right:0;height:1px;background:var(--line)}
.row .sq{width:30px;height:30px;border-radius:8px}
.row .t{flex:1;min-width:0} .row .t b{display:block;font-weight:500;font-size:17px} .row .t span{display:block;color:var(--ink2);font-size:14px;line-height:1.35}
.row .d{color:var(--ink3);font-size:15px}
.row .cv{color:#c4c4c7}
.row img{width:44px;height:44px;border-radius:50%;background:#eef3f8;object-fit:contain;flex:none}
.row + .row.av::before{left:74px}
.foot{display:none}
@media (max-width:900px){.shell{grid-template-columns:1fr}.side{display:none}.content{padding:28px 16px 60px}.lt{font-size:34px}}
`, `<div class="shell">
<aside class="side">
  <div class="logo"><img src="img/dobrograd-mark.svg" alt=""><span>ОС будблоку<small>Iron Invest · Доброград</small></span></div>
  <div class="s">${ico('search', 15)}Пошук</div>
  <h6>${esc(N.groupWork)}</h6>
  <a class="it on" href="#"><span class="sq" style="background:#8e8e93">${ico('doc', 14, 2)}</span>${esc(N.home)}</a>
  ${SECTIONS.slice(0, 5).map((s) => `<a class="it" href="#"><span class="sq" style="background:${s.tint}">${ico(s.ico, 14, 2)}</span>${esc(s.label)}</a>`).join('')}
  <h6>${esc(N.groupBase)}</h6>
  <a class="it" href="#"><span class="sq" style="background:#8e8e93">${ico('book', 14, 2)}</span>${esc(N.kernel)}</a>
  <a class="it" href="#"><span class="sq" style="background:#30b0c7">${ico('route', 14, 2)}</span>${esc(N.regulation)}</a>
  <a class="it" href="#"><span class="sq" style="background:#a2845e">${ico('cal', 14, 2)}</span>${esc(N.roadmap)}</a>
</aside>
<main class="content">
  <h1 class="lt">Будівельний блок</h1>
  <p class="lead">${dash(H.heroLead)}</p>
  <div class="sb">${ico('search', 17)}${esc(H.searchTitle)}</div>
  <div class="gh">${esc(H.startTitle)}</div>
  <div class="grp">${H.start.map((c, i) => `<a class="row" href="#"><span class="sq" style="background:${['#0071e3', '#34a853', '#ff9500'][i]}">${ico(['users', 'doc', 'route'][i], 17, 2)}</span><span class="t"><b>${esc(c.title)}</b><span>${esc(c.text)}</span></span><span class="cv">${ico('chev', 16, 2.4)}</span></a>`).join('')}</div>
  <div class="gh">${esc(H.rolesTitle)}</div>
  <div class="grp">${main.slice(0, 6).map((r) => `<a class="row av" href="#"><img src="img/role-${r.slug}.webp" alt=""><span class="t"><b>${esc(r.title)}</b><span>${dash(cap(r.short))}</span></span><span class="cv">${ico('chev', 16, 2.4)}</span></a>`).join('')}
    <a class="row" href="#"><span class="t"><b class="link">Усі 14 ролей</b></span><span class="cv">${ico('chev', 16, 2.4)}</span></a></div>
  <div class="gh">${esc(H.actionsTitle)}</div>
  <div class="grp">${H.actions.slice(0, 4).map((a, i) => `<a class="row" href="#"><span class="sq" style="background:${['#34a853', '#5856d6', '#ff3b30', '#ff9500'][i]}">${ico(['doc', 'check', 'cal', 'coins'][i], 17, 2)}</span><span class="t"><b>${esc(a.title)}</b><span>${esc(a.text)}</span></span><span class="cv">${ico('chev', 16, 2.4)}</span></a>`).join('')}</div>
</main></div>`);

/* ===================== C · Support ===================== */
const C = page('C · Підтримка', `
.hero{text-align:center;padding-block:80px 56px}
.hero img.mk{height:56px}
.hero h1{margin:18px 0 0;font:600 clamp(36px,5vw,56px)/1.07 var(--display);letter-spacing:-.033em}
.hero p{margin:12px auto 0;max-width:560px;color:var(--ink2);font-size:19px}
.sbox{margin:30px auto 0;max-width:640px;display:flex;align-items:center;gap:12px;height:56px;padding:0 20px;border-radius:14px;border:1px solid #d2d2d7;color:var(--ink3);font-size:17px;text-align:left;transition:border-color .2s var(--ease),box-shadow .2s var(--ease)}
.sbox:hover{border-color:#86868b;box-shadow:0 4px 18px rgba(0,0,0,.06)}
.cats{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;padding-block:12px 72px}
.cat{display:flex;flex-direction:column;align-items:center;gap:12px;padding:12px 4px;border-radius:18px;text-align:center;font-size:14px;letter-spacing:-.01em}
.cat .c{width:88px;height:88px;border-radius:50%;background:var(--bg2);display:grid;place-items:center;transition:transform .3s var(--ease),background .2s ease}
.cat:hover .c{transform:scale(1.05);background:#ebebef}
.cat small{color:var(--ink3);font-size:12px;margin-top:-8px}
.sec{border-top:1px solid var(--line);padding-block:56px}
.sec h2{margin:0;font:600 32px/1.12 var(--display);letter-spacing:-.028em;text-align:center}
.pop{margin:32px auto 0;max-width:820px;display:grid;grid-template-columns:1fr 1fr;column-gap:48px}
.pop a{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 2px;border-bottom:1px solid var(--line);font-size:17px}
.pop a span small{display:block;color:var(--ink2);font-size:14px;margin-top:2px}
.pop a svg{color:var(--link);flex:none}
.pop a:hover b{color:var(--link)} .pop b{font-weight:500}
.ppl{margin-top:36px;display:grid;grid-template-columns:repeat(4,1fr);gap:28px 16px}
.pp{display:flex;flex-direction:column;align-items:center;text-align:center;gap:10px;font-size:15px}
.pp img{width:120px;height:120px;border-radius:50%;background:var(--bg2);object-fit:contain;padding:8px;transition:transform .3s var(--ease)}
.pp:hover img{transform:scale(1.04)} .pp span{max-width:200px}
.dark{background:#000;color:#f5f5f7;text-align:center;padding:96px 22px}
.dark q{display:block;font:600 clamp(28px,4vw,48px)/1.1 var(--display);letter-spacing:-.03em;quotes:none}
.dark p{margin:14px 0 0;color:#86868b}
.dark .btn{margin-top:28px}
@media (max-width:833px){.cats{grid-template-columns:repeat(3,1fr)}.pop{grid-template-columns:1fr}.ppl{grid-template-columns:repeat(2,1fr)}.cat .c{width:72px;height:72px}}
`, `${gnav()}
<main>
<section class="hero wrap">
  <img class="mk" src="img/dobrograd-mark.svg" alt="">
  <h1>Чим допомогти?</h1>
  <p>Регламенти, форми і строки будівельного блоку.</p>
  <a class="sbox" href="#">${ico('search', 19)}<span>${esc(H.searchTitle)}</span></a>
</section>
<section class="wrap cats">${SECTIONS.map((s) => `<a class="cat" href="#"><span class="c" style="color:${s.tint}">${ico(s.ico, 34, 1.5)}</span>${esc(s.label)}<small>${esc(s.sub)}</small></a>`).join('')}</section>
<section class="sec wrap"><h2>Популярне</h2>
  <div class="pop">${H.actions.map((a) => `<a href="#"><span><b>${esc(a.title)}</b><small>${esc(a.text)}</small></span>${ico('chev', 16, 2.2)}</a>`).join('')}</div>
</section>
<section class="sec wrap"><h2>Ваша роль</h2>
  <div class="ppl">${main.map((r) => `<a class="pp" href="#"><img src="img/role-${r.slug}.webp" alt=""><span>${esc(r.title)}</span></a>`).join('')}</div>
  <p style="text-align:center;margin:36px 0 0"><a class="link" href="#">Усі 14 ролей ›</a></p>
</section>
<section class="dark"><q>${esc(U.site.motto)}</q><p>Не знайшли потрібне? Напишіть, додамо в базу.</p><a class="btn" href="#">Написати в Telegram</a></section>
</main>${foot()}`);

const out = new URL('./', import.meta.url);
fs.writeFileSync(new URL('a.html', out), A);
fs.writeFileSync(new URL('b.html', out), B);
fs.writeFileSync(new URL('c.html', out), C);
console.log('ok', main.length, 'roles');
