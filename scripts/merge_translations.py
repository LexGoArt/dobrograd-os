# -*- coding: utf-8 -*-
"""Збирає переклади з scratchpad/tr/<lang>/ у src/data/<lang>/ і звіряє структуру з uk."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SP = '/private/tmp/claude-501/-Users-alexgo-Desktop-design-test/b0ad535e-a3c5-482e-be7e-4172bb9bf637/scratchpad/tr'
GROUPS = ['А', 'Б', 'В', 'Г', 'Д', 'Е']
PROTECTED_DOC = ['index', 'slug', 'group', 'status', 'drive']

def shape(x, path=''):
    """Рекурсивний «скелет» структури: ключі + типи (без значень)."""
    if isinstance(x, dict):
        return {k: shape(v, f'{path}.{k}') for k, v in sorted(x.items())}
    if isinstance(x, list):
        return [len(x)] + ([shape(x[0], path + '[]')] if x else [])
    return type(x).__name__

problems = []

def check(uk_obj, tr_obj, name, lang):
    if shape(uk_obj) != shape(tr_obj):
        problems.append(f'{lang}/{name}: структура відрізняється від uk')

for lang in ['ru', 'en']:
    out_dir = os.path.join(ROOT, 'src', 'data', lang)
    os.makedirs(out_dir, exist_ok=True)
    src = lambda n: json.load(open(f'{SP}/{lang}/{n}'))
    uk = lambda n: json.load(open(f'{SP}/uk/{n}'))

    # docs.json
    docs = []
    for g in GROUPS:
        chunk = src(f'docs-{g}.json')
        check(uk(f'docs-{g}.json'), chunk, f'docs-{g}', lang)
        for d_uk, d_tr in zip(uk(f'docs-{g}.json'), chunk):
            for key in PROTECTED_DOC:
                if d_uk.get(key) != d_tr.get(key):
                    problems.append(f'{lang}/docs-{g}: {d_uk["index"]} змінене захищене поле {key}')
                    d_tr[key] = d_uk[key]
            d_tr['rhythm'] = d_uk['rhythm']
            d_tr['related'] = d_uk['related']
        docs.extend(chunk)
    json.dump(docs, open(f'{out_dir}/docs.json', 'w'), ensure_ascii=False, indent=1)

    # kernel.json
    meta = src('kernel-meta.json')
    chapters = [src(f'kernel-{i}.json') for i in range(1, 6)]
    for i in range(1, 6):
        check(uk(f'kernel-{i}.json'), chapters[i-1], f'kernel-{i}', lang)
    json.dump({'title': meta['title'], 'subtitle': meta['subtitle'], 'chapters': chapters},
              open(f'{out_dir}/kernel.json', 'w'), ensure_ascii=False, indent=1)

    # roles.json
    roles = src('roles-1.json') + src('roles-2.json')
    uk_roles = uk('roles-1.json') + uk('roles-2.json')
    for r_uk, r_tr in zip(uk_roles, roles):
        for key in ['slug', 'group', 'icon', 'submits', 'receives']:
            if r_uk.get(key) != r_tr.get(key):
                problems.append(f'{lang}/roles: {r_uk["slug"]} змінене захищене поле {key}')
                r_tr[key] = r_uk[key]
        for s_uk, s_tr in zip(r_uk['sections'], r_tr['sections']):
            if s_uk['title'] != s_tr['title']:
                problems.append(f'{lang}/roles: {r_uk["slug"]} перекладений службовий title секції')
                s_tr['title'] = s_uk['title']
        for c_uk, c_tr in zip(r_uk['chain'], r_tr['chain']):
            c_tr['slug'] = c_uk['slug']; c_tr['icon'] = c_uk['icon']
    json.dump(roles, open(f'{out_dir}/roles.json', 'w'), ensure_ascii=False, indent=1)

    # прості файли
    for name in ['calendar', 'regulation', 'checklists', 'processes']:
        d = src(f'{name}.json')
        check(uk(f'{name}.json'), d, name, lang)
        if name == 'processes':
            for p_uk, p_tr in zip(uk('processes.json'), d):
                p_tr['slug'] = p_uk['slug']; p_tr['icon'] = p_uk['icon']; p_tr['docs'] = p_uk['docs']
        if name == 'checklists':
            for c_uk, c_tr in zip(uk('checklists.json'), d):
                c_tr['id'] = c_uk['id']; c_tr['source'] = c_uk['source']
        json.dump(d, open(f'{out_dir}/{name}.json', 'w'), ensure_ascii=False, indent=1)

    # misc -> routes.json + dict.json
    misc = src('misc.json')
    json.dump(misc['routes'], open(f'{out_dir}/routes.json', 'w'), ensure_ascii=False, indent=1)
    d = misc['dict']
    for idx, entry in d['indexes'].items():
        entry['slug'] = uk('misc.json')['dict']['indexes'][idx]['slug']
    json.dump(d, open(f'{out_dir}/dict.json', 'w'), ensure_ascii=False, indent=1)

if problems:
    print('ПРОБЛЕМИ (виправлено автоматично, але переглянь):')
    for p in problems: print(' -', p)
else:
    print('Структура ідеальна, розбіжностей немає.')
print('MERGED ru+en -> src/data/')
