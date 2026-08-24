# -*- coding: utf-8 -*-
"""Конвейер контенту: content/*.json (дампи Excel) -> src/data/uk/*.json.

Тут же застосовуються виправлення аудиту (AUDIT.md), підтверджені Alex 23.08.2026:
терміни, уніфікація «відділ закупівель», одруківки, ліміти, рядок маркетингу у взаємодії КП.
"""
import json, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = lambda *p: os.path.join(ROOT, 'content', *p)
OUT = os.path.join(ROOT, 'src', 'data', 'uk')
os.makedirs(OUT, exist_ok=True)

kernel = json.load(open(C('kernel_v7.json')))
simplified = json.load(open(C('simplified_drive.json')))
forms = json.load(open(C('forms.json')))
drive = json.load(open(os.path.join(ROOT, 'drive-links.json')))

# ---------- Аудит-виправлення тексту ----------
PRE_FIXES = [
    # п.9: у взаємодії КП «комерційний блок» означає продажі
    ('Комерційний блок - терміни готовності, презентаційний стан обʼєкта, вплив на продажі',
     'Маркетинг і продажі - терміни готовності, презентаційний стан обʼєкта, вплив на продажі'),
]
FIXES = [
    ('Технологічний нагляд', 'Технічний нагляд'),                     # п.7
    ('комерційному блоку', 'відділу закупівель'),                     # п.8
    ('комерційного блоку', 'відділу закупівель'),
    ('комерційний блок', 'відділ закупівель'),
    ('Комерційний блок', 'Відділ закупівель'),
    ('Комерційний відділ', 'Відділ закупівель'),
    ('комерційний відділ', 'відділ закупівель'),
    ('Комерційний (постачання як внутрішній підрядник)', 'Відділ закупівель (постачання як внутрішній підрядник)'),
    ('до ______ грн', 'до ліміту (суму встановлює ГД)'),              # п.15
    ('понад ______ грн', 'понад ліміт (суму встановлює ГД)'),
    ('понад ___% від суми договору', 'понад норму (відсоток встановлює ГД)'),
    ('понад ___% суми договору', 'понад норму (відсоток встановлює ГД)'),
]
SIMPLIFIED_FIXES = [
    # п.5: строки перевірки ВТВ -> абсолютні дедлайни
    ('ВТВ перевіряє план протягом 2 робочих днів:', 'ВТВ перевіряє план до 28 числа:'),
    ('ВТВ протягом 2 робочих днів перевіряє фактичні обсяги', 'ВТВ до 10 числа перевіряє фактичні обсяги'),
    ('Перевіряє і погоджує місячні плани та графіки робіт (2 робочі дні).',
     'Перевіряє і погоджує місячні плани та графіки робіт (до 28 числа).'),
    # п.10: модель лімітів замість «ГД затверджує весь реєстр»
    ('Керівник служби замовника формує реєстр на оплату лише з перевірених ВТВ актів, у межах лімітів повноважень; передає реєстр Генеральному директору.',
     'Керівник служби замовника формує реєстр на оплату лише з перевірених ВТВ актів і затверджує платежі в межах свого ліміту.'),
    ('Генеральний директор затверджує реєстр; фінансова служба проводить розрахунки протягом 3 робочих днів.',
     'Генеральний директор затверджує платежі понад ліміт та будь-які платежі поза затвердженим кошторисом (лише за запитом на зміну Г1); фінансова служба проводить розрахунки протягом 3 робочих днів.'),
]

def fix_text(s, extra=()):
    for a, b in PRE_FIXES: s = s.replace(a, b)
    for a, b in extra: s = s.replace(a, b)
    for a, b in FIXES: s = s.replace(a, b)
    return s

def fix_rows(rows, extra=()):
    out = []
    for r in rows:
        cells = {k: fix_text(v, extra) for k, v in r['cells'].items()}
        out.append({'row': r['row'], 'cells': cells})
    return out

# п.11: матриця повноважень, рядок АПР - виконавець готує акт, технагляд затверджує
for r in kernel['Технічний блок']:
    vals = list(r['cells'].values())
    if vals and vals[0].startswith('Приймання прихованих робіт'):
        ks = sorted(r['cells'], key=int)
        if len(ks) >= 3:
            r['cells'][ks[2]] = 'Нач. дільниці / прораб'

kernel = {k: fix_rows(v) for k, v in kernel.items()}
simplified = {k: fix_rows(v, SIMPLIFIED_FIXES) for k, v in simplified.items()}
for d in forms.values():
    d['sheets'] = {k: fix_rows(v) for k, v in d['sheets'].items()}

# ---------- Довідник документів ----------
GROUPS = {
    'А': 'Календар', 'Б': 'Місячний цикл', 'В': 'Ресурси і закупівлі',
    'Г': 'Якість, зміни, фіксація', 'Д': 'Чек-листи', 'Е': 'Регламенти',
}
TRANSLIT = {'А':'a','Б':'b','В':'v','Г':'g','Д':'d','Е':'e'}
def slug_of(idx): return TRANSLIT[idx[0]] + idx[1:]

READY = {'А','Б1','Б2','Б3','В1','В2','В3','В4','В5','В6','В7','Г1','Г3','Г4','Г7','Г8','Г9','Д1','Д2','Д3','Д4','Е1','Е3'}

# Реєстр v7 - назви і призначення
REG = {}
for r in kernel['Реєстр додатків']:
    cells = [v for _, v in sorted(r['cells'].items(), key=lambda x: int(x[0]))]
    if len(cells) >= 4 and re.match(r'^[АБВГДЕ]\d?$', cells[1]):
        REG[cells[1]] = {'name': cells[2], 'purpose': cells[3]}

# Потоки: хто -> кому -> коли (+санкція) - з Календаря А та інструкцій форм
FLOWS = {
 'А':  dict(frm='ВТВ / Керівник СЗ', to='усі ролі технічного блоку', term='постійно діючий довідник', rhythm=['довідник'],
            sanction='Звіт, не поданий у строк, вважається неподаним - автоматична ескалація.'),
 'Б1': dict(frm='Начальник дільниці', to='ВТВ', term='до 25 числа щомісяця', rhythm=['щомісяця'],
            sanction='Немає плану - наступний місяць не фінансується і матеріали не замовляються.'),
 'Б2': dict(frm='Начальник дільниці', to='ВТВ (погоджує), Керівник СЗ (затверджує)', term='до 25 числа; статус план-факт - щопʼятниці до 17:00', rhythm=['щомісяця','щотижня'],
            sanction='Тиждень без статусу - роботи тижня не приймаються до місячного закриття.'),
 'Б3': dict(frm='Начальник дільниці', to='ВТВ', term='до 5 числа наступного місяця', rhythm=['щомісяця'],
            sanction='Один відсутній документ або підпис - пакет не прийнятий, оплата не розглядається.'),
 'В1': dict(frm='Прораб / начальник дільниці', to='ВТВ → відділ закупівель', term='зведена потреба - до 25 числа; поточні - за строком поставки', rhythm=['щомісяця','за фактом'],
            sanction='Пізня заявка не гарантує матеріал вчасно - простій лягає на заявника.'),
 'В2': dict(frm='Прораб / начальник дільниці', to='механік → Керівник проєкту', term='відповідь - 1 робочий день', rhythm=['за фактом'],
            sanction='Простій замовленої техніки з вини заявника фіксується у табелі і розбирається.'),
 'В3': dict(frm='Прораб / начальник дільниці', to='КП → ВТВ → відділ закупівель', term='спецтехніка - разом із заявкою на бетон; різноробочі - за 2 робочі дні', rhythm=['за фактом'],
            sanction='Роботи зовнішніх виконавців без договору чи талонів не оплачуються.'),
 'В4': dict(frm='Механік', to='ВТВ', term='при кожному переміщенні техніки', rhythm=['за фактом'],
            sanction='Логістика і час переміщення без акта не списуються.'),
 'В5': dict(frm='Водій / механік (підписує нач. дільниці)', to='ВТВ', term='заповнюється щозміни; у ВТВ - щопʼятниці до 18:00', rhythm=['щодня','щотижня'],
            sanction='Моточаси і паливо без табеля не списуються.'),
 'В6': dict(frm='Начальник дільниці', to='ВТВ', term='при кожній передачі ТМЦ / техніки', rhythm=['за фактом'], sanction=None),
 'В7': dict(frm='КП + ВТВ', to='КСЗ (погоджує) → ГД (затверджує)', term='до вибору підрядника', rhythm=['за фактом'],
            sanction='Закупівля без 3 пропозицій або вибір без обґрунтування - договір не підписується.'),
 'Г1': dict(frm='Будь-який учасник (ініціатор)', to='ВТВ → КП → КСЗ; поза кошторисом - ГД', term='ДО початку робіт; відповідь - 5 робочих днів', rhythm=['за фактом'],
            sanction='Роботи без зареєстрованої зміни - самовільні і не оплачуються.'),
 'Г2': dict(frm='Начальник дільниці', to='технагляд → ВТВ', term='до закриття робіт наступними', rhythm=['за фактом'],
            sanction='Роботи закриті самовільно - можливе розкриття за рахунок винного.'),
 'Г3': dict(frm='Технагляд', to='нач. дільниці, КП; реєстр - ВТВ', term='не пізніше 1 робочого дня після огляду', rhythm=['за фактом'],
            sanction='Роботи із зауваженням не закриваються до усунення.'),
 'Г4': dict(frm='Технагляд / інженер ТБ / КСЗ', to='КП, нач. дільниці, КСЗ (повідомляє ГД)', term='того ж дня', rhythm=['за фактом'],
            sanction='Простій з вини виконавця не компенсується; збитки - у реєстр претензій.'),
 'Г5': dict(frm='ВТВ (веде постійно)', to='КП, КСЗ, ГД - за запитом', term='оновлення - до 10 числа щомісяця', rhythm=['щомісяця'],
            sanction='Пропущений перебор - відповідальність ВТВ.'),
 'Г6': dict(frm='Нач. дільниці / КП', to='ВТВ', term='паралельно з роботами', rhythm=['за фактом'], sanction=None),
 'Г7': dict(frm='Лаборант', to='технагляд, КСЗ; копія - ВТВ', term='протягом 1 робочого дня після випробування', rhythm=['за фактом'],
            sanction='АПР і приймання конструкцій без протоколу не закриваються.'),
 'Г8': dict(frm='ВТВ + юрист', to='КСЗ (погоджує) → ГД (затверджує) → підрядник', term='за фактом порушення; відповідь підрядника - 5 робочих днів', rhythm=['за фактом'],
            sanction='Утримання з наступних оплат; при невиконанні - розірвання договору.'),
 'Г9': dict(frm='Ініціатор', to='керівник за ланцюгом ескалації', term='за фактом; відповідь - 2 робочі дні', rhythm=['за фактом'], sanction=None),
 'Д1': dict(frm='Керівник СЗ', to='ГД (гейт передачі в реалізацію)', term='до старту проєкту', rhythm=['за фактом'],
            sanction='Без повного стартового пакета проєкт не передається в реалізацію.'),
 'Д2': dict(frm='Керівник СЗ / КП', to='-', term='перед стадією «Реалізація робіт»', rhythm=['за фактом'], sanction=None),
 'Д3': dict(frm='Начальник дільниці', to='-', term='до 25 (план) і до 5 (пакет)', rhythm=['щомісяця'],
            sanction='Нема галочки - оплата місяця під ризиком.'),
 'Д4': dict(frm='Нач. дільниці / прораб', to='-', term='щодня, щотижня і перед кожним АПР', rhythm=['щодня','щотижня'],
            sanction='Роботи без фотофіксації не приймаються.'),
 'Д5': dict(frm='Керівник СЗ', to='ГД', term='щокварталу', rhythm=['за фактом'], sanction=None),
 'Е1': dict(frm='Затверджує ГД', to='ВТВ + дільниця (обовʼязковий)', term='постійно діючий регламент', rhythm=['довідник'], sanction=None),
 'Е2': dict(frm='Затверджує ГД', to='учасники тендерів', term='постійно діючий регламент', rhythm=['довідник'], sanction=None),
 'Е3': dict(frm='Затверджує ГД', to='усі учасники платіжного процесу', term='постійно діючий регламент', rhythm=['довідник'], sanction=None),
 'Е4': dict(frm='Затверджує ГД', to='усі ролі', term='постійно діючий регламент', rhythm=['довідник'], sanction=None),
 'Е5': dict(frm='Затверджує ГД', to='дільниця', term='постійно діючий регламент', rhythm=['довідник'], sanction=None),
 'Е6': dict(frm='Затверджує ГД', to='дільниця, технагляд, ВТВ', term='постійно діючий регламент', rhythm=['довідник'], sanction=None),
 'Е7': dict(frm='Затверджує ГД', to='лаборант, технагляд', term='постійно діючий регламент', rhythm=['довідник'], sanction=None),
 'Е8': dict(frm='Затверджує ГД', to='технагляд, дільниця', term='постійно діючий регламент', rhythm=['довідник'], sanction=None),
 'Е9': dict(frm='Затверджує ГД', to='дільниця, ВТВ, кошторисник', term='постійно діючий регламент', rhythm=['довідник'], sanction=None),
}

DEV_OWNER = {  # хто винен за документ у розробці
    'Г2': 'ВТВ (спитати готові шаблони)', 'Г5': 'ВТВ (спитати діючу форму)', 'Г6': 'ВТВ (що вже використовують)',
    'Д5': 'Операційний блок', 'Е1': None, 'Е2': 'Операційний блок', 'Е4': 'Операційний блок',
    'Е5': 'Операційний блок', 'Е6': 'ВТВ + операційний блок', 'Е7': 'Операційний блок',
    'Е8': 'Перший драфт готує Claude', 'Е9': 'ВТВ + кошторисник',
}

# ---------- Генератор блоків з листа ----------
def rows_to_blocks(rows):
    blocks, i = [], 0
    rows = [r for r in rows if r['cells']]
    def cellvals(r): return [v for _, v in sorted(r['cells'].items(), key=lambda x: int(x[0]))]
    while i < len(rows):
        vals = cellvals(rows[i])
        if len(vals) == 1:
            t = vals[0]
            if re.match(r'^[\d\s._☐-]+$', t):  # порожні рядки бланків
                i += 1; continue
            letters = [c for c in t if c.isalpha()]
            caps = letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.6
            short_head = len(t) < 45 and not t.endswith(('.', ':', ';')) and rows[i]['row'] > 2 \
                and i + 1 < len(rows) and len(cellvals(rows[i+1])) > 1
            is_h = (len(t) < 90 and caps) or short_head
            blocks.append({'t': 'h' if is_h else 'p', 'text': t})
            i += 1
            continue
        # група багатоколонкових рядків
        group = []
        while i < len(rows) and len(cellvals(rows[i])) > 1:
            group.append(cellvals(rows[i])); i += 1
        # список: усі рядки з 2 колонок і перша - номер/маркер
        if all(len(g) == 2 and re.match(r'^(\d+|•|!|-|☐)$', g[0]) for g in group):
            kind = 'note' if group[0][0] == '!' else 'ol' if group[0][0].isdigit() else 'ul'
            if kind == 'note':
                for g in group: blocks.append({'t': 'note', 'text': g[1]})
            else:
                blocks.append({'t': kind, 'items': [g[1] for g in group]})
        else:
            header = None
            if re.match(r'^(№|Роль|Термін|Скорочення|Процес|Прострочення|Документ|Звіт|Реєстр|Журнал|Крок|Умова|Порушення|Подія|Версія|Що)', group[0][0]) and len(group) > 1:
                header = group[0]; group = group[1:]
            notes = [g for g in group if g[0] == '!']
            group = [g for g in group if g[0] != '!']
            if group:
                width = max(len(g) for g in group + ([header] if header else []))
                blocks.append({'t': 'table',
                               'header': (header + [''] * (width - len(header))) if header else None,
                               'rows': [g + [''] * (width - len(g)) for g in group]})
            for n in notes: blocks.append({'t': 'note', 'text': n[1]})
    return blocks

# ---------- Автолінковка ----------
def build_dict():
    d = {}
    for idx in FLOWS:
        d[idx] = {'slug': slug_of(idx), 'name': REG.get(idx, {}).get('name', idx)}
    return d
LINKDICT = build_dict()

def scan_related(blocks, self_idx):
    text = json.dumps(blocks, ensure_ascii=False)
    found = set()
    for idx in LINKDICT:
        if idx == self_idx or idx == 'А': continue
        if re.search(r'(?<![А-ЯЁІЇЄҐа-яёіїєґ\d])' + idx + r'(?![0-9])', text):
            found.add(idx)
    for term, idx in [('технічна довідка', 'Е3'), ('Технічна довідка', 'Е3'),
                      ('накопичувальн', 'Г5'), ('Накопичувальн', 'Г5')]:
        if idx != self_idx and term in text: found.add(idx)
    return sorted(found, key=lambda x: (x[0], x[1:]))

# ---------- docs.json ----------
docs = []
for idx, flow in FLOWS.items():
    status = 'ready' if idx in READY else 'dev'
    entry = {
        'index': idx, 'slug': slug_of(idx),
        'name': REG.get(idx, {}).get('name', ''), 'purpose': REG.get(idx, {}).get('purpose', ''),
        'group': idx[0], 'groupName': GROUPS[idx[0]],
        'status': status, 'devOwner': DEV_OWNER.get(idx),
        'drive': drive['docs'].get(idx),
        'updated': drive.get('updated', {}).get(idx),
        'from': flow['frm'], 'to': flow['to'], 'term': flow['term'],
        'rhythm': flow['rhythm'], 'sanction': flow['sanction'],
        'sections': [], 'related': [],
    }
    f = forms.get(idx)
    if f:
        for sheet, rows in f['sheets'].items():
            entry['sections'].append({'title': sheet, 'blocks': rows_to_blocks(rows)})
    entry['related'] = scan_related(entry['sections'], idx) if entry['sections'] else []
    docs.append(entry)
json.dump(docs, open(os.path.join(OUT, 'docs.json'), 'w'), ensure_ascii=False, indent=1)

# ---------- calendar.json ----------
cal_rows = forms['А']['sheets']['Календар звітності']
cal = {'title': '', 'intro': '', 'sections': [], 'outro': []}
cur = None
for r in cal_rows:
    vals = [v for _, v in sorted(r['cells'].items(), key=lambda x: int(x[0]))]
    if len(vals) == 1:
        t = vals[0]
        if r['row'] == 1: cal['title'] = t
        elif r['row'] == 2: cal['intro'] = t
        elif t.upper() == t and len(t) < 60:
            cur = {'rhythm': t, 'items': [], 'note': None}
            cal['sections'].append(cur)
        elif cur: cur['note'] = t if not cur['items'] or r['row'] < 43 else cur['note']; (cal['outro'].append(t) if r['row'] >= 43 else None)
        continue
    if vals[0] == '№': continue
    if cur and len(vals) >= 6:
        cur['items'].append({'num': vals[0], 'what': vals[1], 'from': vals[2], 'to': vals[3],
                             'term': vals[4], 'form': vals[5], 'sanction': vals[6] if len(vals) > 6 else ''})
json.dump(cal, open(os.path.join(OUT, 'calendar.json'), 'w'), ensure_ascii=False, indent=1)

# ---------- roles.json ----------
K = kernel['Технічний блок']
def kv(r): return [v for _, v in sorted(r['cells'].items(), key=lambda x: int(x[0]))]

ROLE_BOUNDS = [
    ('ksz', 'КЕРІВНИК СЛУЖБИ ЗАМОВНИКА', 'Керівник служби замовника'),
    ('proektna-grupa', 'ПРОЕКТНА ГРУПА (АУТСОРС)', 'Проєктна група (аутсорс)'),
    ('vtv', 'КЕРІВНИК ВТВ', 'Керівник ВТВ'),
    ('koshtorysnyk', 'КОШТОРИСНИК (ПІД КЕРІВНИКОМ ВТВ)', 'Кошторисник'),
    ('tehnahliad', 'ТЕХНІЧНИЙ НАГЛЯД', 'Технічний нагляд'),
    ('mehanik', 'МЕХАНІК', 'Механік'),
    ('inzhener-tb', 'ІНЖЕНЕР З ОХОРОНИ ПРАЦІ / ТБ (АУТСОРС)', 'Інженер з охорони праці / ТБ (аутсорс)'),
    ('laborant', 'ЛАБОРАНТ (АУТСОРС)', 'Лаборант (аутсорс)'),
    ('kp', 'КЕРІВНИК ПРОЄКТУ', 'Керівник проєкту'),
    ('nachalnyk-dilnytsi', 'НАЧАЛЬНИК ДІЛЬНИЦІ', 'Начальник дільниці'),
    ('prorab', 'ПРОРАБ', 'Прораб'),
    ('brygady', 'РОБОЧІ БРИГАДИ', 'Робочі бригади'),
]
STOP_HEADS = {b[1] for b in ROLE_BOUNDS} | {'ШТАБ ПРОЄКТУ', 'ВИКОНАВЦІ', 'KPI ПО РОЛЯХ', 'СЛУЖБА ЗАМОВНИКА'}

idx_by_head = {}
for i, r in enumerate(K):
    vals = kv(r)
    if len(vals) == 1 and vals[0] in STOP_HEADS:
        idx_by_head.setdefault(vals[0], i)

roles = []
for slug, head, title in ROLE_BOUNDS:
    start = idx_by_head[head] + 1
    end = len(K)
    for h, j in idx_by_head.items():
        if j > idx_by_head[head]: end = min(end, j)
    seg = K[start:end]
    sections, cursec = [], None
    for r in seg:
        vals = kv(r)
        if len(vals) == 1 and vals[0] in ('Зона відповідальності', 'Обовʼязки', 'Взаємодія'):
            cursec = {'title': vals[0], 'items': []}
            sections.append(cursec); continue
        if len(vals) == 1 and cursec is None:
            sections.append({'title': '', 'items': [vals[0]]}); continue
        if cursec is not None:
            cursec['items'].append(vals[-1] if len(vals) > 1 else vals[0])
    roles.append({'slug': slug, 'title': title, 'sections': sections, 'kpi': None,
                  'group': 'Служба замовника' if slug in ('ksz','proektna-grupa','vtv','koshtorysnyk','tehnahliad','mehanik','inzhener-tb','laborant') else 'Штаб проєкту'})

# ГД і відділ закупівель - зі спрощеного
S = simplified['Схема']
def srange(a, b):
    return [kv(r)[0] for r in S if a <= r['row'] <= b]
roles.insert(0, {'slug': 'gd', 'title': 'Генеральний директор', 'group': 'Керівництво',
                 'sections': [{'title': 'Зона відповідальності', 'items': [t.lstrip('• ') for t in srange(40, 42)]}], 'kpi': None})
roles.append({'slug': 'zakupivli', 'title': 'Відділ закупівель (комерційний блок)', 'group': 'Сервісні підрозділи',
              'sections': [{'title': 'Зона відповідальності', 'items': [t.lstrip('• ') for t in srange(64, 66)]}], 'kpi': None})

# KPI
kpi_start = idx_by_head['KPI ПО РОЛЯХ']
for r in K[kpi_start+1:kpi_start+14]:
    vals = kv(r)
    if len(vals) == 2 and vals[0] != 'Роль':
        for role in roles:
            key = vals[0].lower().replace('керівник ', '').strip()
            if key in role['title'].lower() or vals[0].lower() in role['title'].lower():
                role['kpi'] = vals[1]

# документи ролі: подає / отримує
ROLE_KEYS = {
    'gd': ['ГД'], 'ksz': ['КСЗ', 'Керівник СЗ'], 'vtv': ['ВТВ'], 'koshtorysnyk': ['Кошторисник', 'кошторисник'],
    'tehnahliad': ['Технагляд', 'технагляд'], 'mehanik': ['Механік', 'механік'], 'inzhener-tb': ['інженер ТБ', 'Інженер'],
    'laborant': ['Лаборант', 'лаборант'], 'kp': ['КП', 'Керівник проєкту'], 'nachalnyk-dilnytsi': ['Начальник дільниці', 'начальник дільниці', 'нач. дільниці', 'Нач. дільниці'],
    'prorab': ['Прораб', 'прораб'], 'brygady': [], 'proektna-grupa': [], 'zakupivli': ['відділ закупівель', 'Відділ закупівель'],
}
for role in roles:
    keys = ROLE_KEYS.get(role['slug'], [])
    subm, recv = [], []
    for d in docs:
        if 'довідник' in d['rhythm']: continue
        if any(k in d['from'] for k in keys): subm.append(d['index'])
        if any(k in d['to'] for k in keys): recv.append(d['index'])
    role['submits'] = subm; role['receives'] = recv
json.dump(roles, open(os.path.join(OUT, 'roles.json'), 'w'), ensure_ascii=False, indent=1)

# ---------- kernel.json (5 глав) ----------
CHAPTERS = []
cur = None
for r in K:
    vals = kv(r)
    if len(vals) == 1 and re.match(r'^\d+\.\s', vals[0]):
        cur = {'num': vals[0].split('.')[0], 'title': vals[0], 'rows': []}
        CHAPTERS.append(cur); continue
    if cur is not None: cur['rows'].append(r)

MAJOR_HEADS = re.compile(r'^(СТРУКТУРА СЛУЖБИ|ЦІЛЬ СЛУЖБИ|РОЛІ ТА ЗОНИ|KPI ПО РОЛЯХ|МАТРИЦЯ ПОВНОВАЖЕНЬ|ВІДПОВІДАЛЬНІСТЬ|ПЕРЕДПРОЄКТНА ПІДГОТОВКА|ПОСЛІДОВНІСТЬ РЕАЛІЗАЦІЇ|МЕХАНІКИ ТА РЕГЛАМЕНТИ|ПРИХОВАНІ РОБОТИ|ПРАВО ЗУПИНЕННЯ|НОРМАТИВНІ СТРОКИ|МАРШРУТИ ЗАПИТІВ|ВЗАЄМОДІЯ З СУМІЖНИМИ|ЕСКАЛАЦІЯ ПРОСТРОЧОК|ДОКУМЕНТООБІГ|РЕЄСТРИ ТА ЖУРНАЛИ|СИСТЕМА ЗВІТНОСТІ|МІСЯЧНИЙ ЦИКЛ|ПРИКІНЦЕВІ ПОЛОЖЕННЯ|ТЕРМІНИ ТА СКОРОЧЕННЯ)')
kernel_out = []
for ch in CHAPTERS:
    blocks = rows_to_blocks(ch['rows'])
    for b in blocks:
        if b['t'] == 'h' and MAJOR_HEADS.match(b['text']):
            b['major'] = True
    kernel_out.append({'num': ch['num'], 'title': re.sub(r'^\d+\.\s*', '', ch['title']),
                       'blocks': blocks})
json.dump({'title': 'Положення про службу замовника',
           'subtitle': kv(K[1])[0] if len(kv(K[1])) else '',
           'chapters': kernel_out},
          open(os.path.join(OUT, 'kernel.json'), 'w'), ensure_ascii=False, indent=1)

# ---------- regulation.json (спрощений) ----------
reg_rows = [r for r in simplified['Регламент'] if r['row'] >= 4]
json.dump({'title': kv(simplified['Регламент'][0])[0],
           'blocks': rows_to_blocks(reg_rows)},
          open(os.path.join(OUT, 'regulation.json'), 'w'), ensure_ascii=False, indent=1)

# ---------- checklists.json ----------
def parse_checklist(rows, cid, title, source):
    intro = ''
    sections, cursec = [], None
    for r in rows:
        vals = [ (k,v) for k,v in sorted(r['cells'].items(), key=lambda x:int(x[0])) ]
        flat = [v for _, v in vals]
        if r['row'] == 2 and len(flat) == 1: intro = flat[0]; continue
        if len(flat) == 1:
            t = flat[0]
            letters = [c for c in t if c.isalpha()]
            if letters and sum(1 for c in letters if c.isupper())/len(letters) > 0.6 and len(t) < 80:
                cursec = {'title': t, 'items': []}; sections.append(cursec)
            continue
        if flat[0] == '№': continue
        if '☐' in flat:
            num = flat[0] if re.match(r'^\d+$', flat[0]) else ''
            cand = [x for x in flat if x not in ('☐', num) and x]
            if not cand: continue
            text = max(cand, key=len)
            meta = ' · '.join(x for x in cand if x != text)
            if cursec is None:
                cursec = {'title': '', 'items': []}; sections.append(cursec)
            cursec['items'].append({'num': num, 'text': text, 'meta': meta})
    return {'id': cid, 'title': title, 'intro': intro, 'source': source, 'sections': sections}

checklists = []
for idx, cid in [('Д1','d1'), ('Д2','d2'), ('Д3','d3'), ('Д4','d4')]:
    rows = forms[idx]['sheets']['Чек-лист']
    checklists.append(parse_checklist(rows, cid, REG[idx]['name'], idx))
checklists.append(parse_checklist(forms['Е1']['sheets']['Чек-лист перевірок ВТВ'], 'vtv',
                                  'Чек-лист перевірок ВТВ (план і звітний пакет)', 'Е1'))
checklists.append(parse_checklist(forms['Б3']['sheets']['Чек-лист комплекту'], 'b3',
                                  'Чек-лист комплекту звітного пакета', 'Б3'))
json.dump(checklists, open(os.path.join(OUT, 'checklists.json'), 'w'), ensure_ascii=False, indent=1)

# ---------- dict.json (автолінковка) ----------
json.dump({'indexes': LINKDICT,
           'terms': {'технічна довідка': 'e3', 'накопичувальна відомість': 'g5', 'реєстр платежів': 'e3'}},
          open(os.path.join(OUT, 'dict.json'), 'w'), ensure_ascii=False, indent=1)

# ---------- routes.json (маршрути запитів) ----------
routes = []
for r in K:
    if 479 <= r['row'] <= 501:
        vals = kv(r)
        if len(vals) == 4:
            routes.append({'what': vals[0], 'who': vals[1], 'whom': vals[2], 'term': vals[3]})
json.dump(routes, open(os.path.join(OUT, 'routes.json'), 'w'), ensure_ascii=False, indent=1)

# ---------- Роль: опис, іконка, «до вас звертаються» / «ви запитуєте», FAQ ----------
ROLE_BOSS = {  # безпосередній керівник (slug); None - вершина
 'gd': None, 'ksz': 'gd', 'vtv': 'ksz', 'koshtorysnyk': 'vtv', 'tehnahliad': 'ksz',
 'mehanik': 'ksz', 'inzhener-tb': 'ksz', 'laborant': 'ksz', 'proektna-grupa': 'ksz',
 'kp': 'ksz', 'nachalnyk-dilnytsi': 'kp', 'prorab': 'nachalnyk-dilnytsi',
 'brygady': 'prorab', 'zakupivli': 'gd',
}
ROLE_META = {
 'gd': dict(icon='building', card='Генеральний директор', short='стратегія, бюджет і рішення вищого рівня',
            tagline='Стратегічне керівництво, бюджет і рішення вищого рівня.'),
 'ksz': dict(icon='compass', card='Керівник СЗ', short='операційне управління службою замовника',
             tagline='Операційне управління службою замовника: від підготовки проєкту до затвердження оплат.'),
 'vtv': dict(icon='folder-check', card='Керівник ВТВ', short='документація і фільтр перед грошима',
             tagline='Єдина точка видачі документації і фільтр перед грошима: перевіряє обсяги, веде накопичувальну відомість, складає технічну довідку.'),
 'koshtorysnyk': dict(icon='calculator', card='Кошторисник', short='кошториси і ціновий контроль',
                      tagline='Кошториси, ціновий контроль і звіт відхилень бюджету.'),
 'tehnahliad': dict(icon='shield-check', card='Технагляд', short='контроль якості та обсягів на майданчику',
                    tagline='Контроль якості та обсягів на майданчику. Без його підпису грошей не отримує ніхто.'),
 'mehanik': dict(icon='wrench', card='Механік', short='техніка, моточаси, паливо і простої',
                 tagline='Техніка, моточаси, паливо і простої - все під приборний облік.'),
 'inzhener-tb': dict(icon='hard-hat', card='Інженер з ОП / ТБ', short='охорона праці, інструктажі і допуски',
                     tagline='Охорона праці: інструктажі, допуски, право зупинити роботи.'),
 'laborant': dict(icon='flask', card='Лаборант', short='незалежні випробування бетону і матеріалів',
                  tagline='Незалежні випробування бетону і матеріалів - підстава закриття прихованих робіт.'),
 'kp': dict(icon='briefcase', card='Керівник проєкту', short='реалізація проєкту в межах бюджету',
            tagline='Реалізація проєкту в межах кошторису, графіка і бюджету.'),
 'nachalnyk-dilnytsi': dict(icon='clipboard-list', card='Начальник дільниці', short='щоденна організація майданчика',
                            tagline='Щоденна організація майданчика: план до 25, звітний пакет до 5, табелі щопʼятниці.'),
 'prorab': dict(icon='hammer', card='Прораб', short='безпосереднє керування роботами',
                tagline='Безпосереднє керування роботами: бригади, журнал робіт, заявки на матеріали.'),
 'brygady': dict(icon='users', card='Робочі бригади', short='виконання робіт за проєктом і нарядом',
                 tagline='Виконання робіт за проєктом, нарядом і технологією.'),
 'proektna-grupa': dict(icon='pencil-ruler', card='Проєктна група', short='проєктні рішення і креслення',
                        tagline='Проєктні рішення, креслення і зміни - через зареєстрований запит.'),
 'zakupivli': dict(icon='package', card='Відділ закупівель', short='постачання за специфікаціями ВТВ',
                   tagline='Постачання матеріалів за специфікаціями ВТВ як внутрішній підрядник.'),
}
ROLE_FAQ = {
 'prorab': [
   ('Що я маю робити щодня?', 'Вести журнал виконання робіт, слідкувати, щоб табель кожної одиниці техніки (В5) заповнювався щозміни, подавати заявки на матеріали (В1) і техніку (В2, В3) заздалегідь.'),
   ('Як замовити матеріали?', 'Заявка В1 з привʼязкою до роботи з плану Б1 - не пізніше строку поставки до дати потреби. Поза планом місяця - лише з обґрунтуванням, а якщо це зміна обсягів - спочатку запит на зміну (Г1).'),
   ('Виявив проблему на майданчику - що робити?', 'Зафіксуй у щоденному зведенні в Telegram-чаті. Якщо потрібна непередбачена робота - жодних «зробимо і потім оформимо»: спочатку начальник дільниці ініціює запит на зміну (Г1), потім робота.'),
   ('Чому мої роботи не прийняли?', 'Найчастіше: немає запису в журналі, немає фотофіксації (Д4), не закритий АПР з протоколами, або робота виконана поза планом без Г1.'),
 ],
 'nachalnyk-dilnytsi': [
   ('Які в мене головні дедлайни?', 'До 8:30 - людність у чат; щопʼятниці до 17:00 - план-факт і фотозвіт, до 18:00 - табелі і накладні; до 25 - план місяця (Б1+Б2+В1); до 5 - звітний пакет (Б3).'),
   ('Що буде, якщо не подати план до 25?', 'Наступний місяць не фінансується і матеріали не замовляються. Це найдорожча помилка місяця.'),
   ('ВТВ повернуло пакет - що далі?', 'У тебе 2 робочі дні на виправлення, потім повторна перевірка 2 дні. Спірні позиції можуть піти на оплату частково - решта після доопрацювання.'),
   ('Як передати ТМЦ чи техніку під відповідальність?', 'Тільки через акт В6. Переміщення техніки між обʼєктами - через акт В4, інакше логістика не списується.'),
 ],
 'vtv': [
   ('Що я перевіряю у плані місяця?', 'Чек-лист блок А: назви за кошторисом, обсяги в межах залишків накопичувальної відомості, відповідність проєкту і змінам Г1, реальність графіка, матеріали за нормами Е9. Строк - до 28 числа.'),
   ('Що робити з перебором?', 'Позиція виключається з підтвердження, начальнику дільниці - письмова вимога пояснення (2 робочі дні). Законна зміна - через Г1 наступним місяцем; без пояснення - не оплачується, Г9, при провині підрядника - Г8.'),
   ('Хто відповідає, якщо перебор пропущено?', 'ВТВ. Розбір причин у Керівника СЗ.'),
 ],
 'kp': [
   ('Як ініціювати платіж?', 'Перевір передумови (договір у реєстрі, кошторис, приймання технаглядом), внеси платіж у реєстр платежів, збери повний пакет за типом платежу і передай у ВТВ. Поза реєстром платежу не існує.'),
   ('Підрядник питає «де мій платіж?»', 'Тільки через тебе: запит статусу через Керівника СЗ, відповідь - 2 робочі дні.'),
   ('Клієнт просить щось змінити - що робити?', 'Побажання клієнтів не йдуть напряму на дільницю. Тільки запит на зміну (Г1) з оцінкою впливу на бюджет і строк.'),
 ],
 'tehnahliad': [
   ('Коли я підписую акти?', 'КБ-2в - щотижня, після перевірки фактичних обсягів. Зауваження після огляду - не пізніше 1 робочого дня (Г3).'),
   ('Мене кличуть закривати приховані роботи - порядок?', 'Огляд ДО закриття наступними роботами, виклик завчасно через Worksection. Перевір фото (Д4), протоколи лаборанта (Г7), сертифікати - без них АПР не приймається.'),
   ('Коли я можу зупинити роботи?', 'Порушення ТБ, відхилення від проєкту, відсутність документації, неякісне виконання, незатверджені матеріали - акт Г4 того ж дня.'),
 ],
 'mehanik': [
   ('Що з табелями техніки?', 'Табель В5 на КОЖНУ одиницю окремо, водій заповнює щозміни, ти щотижня перевіряєш і підписуєш. Без табеля моточаси і паливо не списуються.'),
   ('Техніка їде на інший обʼєкт - що оформити?', 'Акт зміни дислокації В4, інакше переміщення не списується.'),
 ],
 'ksz': [
   ('Які платежі я затверджую?', 'У межах затвердженого кошторису до ліміту (суму встановлює ГД). Понад ліміт і поза кошторисом - ГД, поза кошторисом лише за запитом на зміну Г1.'),
   ('Що я контролюю щомісяця?', 'Технічні довідки ВТВ, вибірково - повернуті пакети і перебори, мінімум 3 пакети оплачених платежів.'),
 ],
}

# ланцюг взаємодії: з Взаємодія-пунктів ролі
CHAIN_ICON = {'генеральний директор':'building','гд':'building','керівник служби':'compass','керівник сз':'compass','ксз':'compass',
 'втв':'folder-check','кошторисник':'calculator','технагляд':'shield-check','механік':'wrench','прораб':'hammer',
 'начальник дільниці':'clipboard-list','нач. дільниці':'clipboard-list','штаб проєкту':'briefcase','керівник проєкту':'briefcase',
 'проєктна група':'pencil-ruler','проектна група':'pencil-ruler','фінансовий блок':'coins','відділ закупівель':'package',
 'бригади':'users','підрядники':'users','лаборант':'flask','інженер':'hard-hat','блок маркетингу':'megaphone','маркетинг':'megaphone',
 'юрист':'scale','технічний нагляд':'shield-check'}
ROLE_BY_KEY = {'генеральний директор':'gd','гд':'gd','керівник служби':'ksz','керівник сз':'ksz','ксз':'ksz','втв':'vtv',
 'кошторисник':'koshtorysnyk','технагляд':'tehnahliad','технічний нагляд':'tehnahliad','механік':'mehanik','прораб':'prorab',
 'начальник дільниці':'nachalnyk-dilnytsi','нач. дільниці':'nachalnyk-dilnytsi','штаб проєкту':'kp','керівник проєкту':'kp',
 'проєктна група':'proektna-grupa','проектна група':'proektna-grupa','відділ закупівель':'zakupivli','бригади':'brygady',
 'підрядники':'brygady','лаборант':'laborant','інженер':'inzhener-tb'}

def chain_for(role):
    out = []
    for sec in role['sections']:
        if sec['title'] != 'Взаємодія': continue
        for item in sec['items']:
            item = item.lstrip('• ').lstrip('| ').strip()
            name = item.split(' - ')[0].strip()
            why = item.split(' - ', 1)[1].strip() if ' - ' in item else ''
            low = name.lower()
            icon, slug = 'users', None
            for key, ic in CHAIN_ICON.items():
                if key in low: icon = ic; slug = ROLE_BY_KEY.get(key); break
            out.append({'name': name, 'why': why, 'icon': icon, 'slug': slug})
    return out

for role in roles:
    meta = ROLE_META.get(role['slug'], {})
    role['icon'] = meta.get('icon', 'users')
    role['cardName'] = meta.get('card', role['title'])
    role['boss'] = ROLE_BOSS.get(role['slug'])
    role['short'] = meta.get('short', '')
    role['tagline'] = meta.get('tagline', '')
    role['chain'] = chain_for(role)
    role['faq'] = [{'q': q, 'a': a} for q, a in ROLE_FAQ.get(role['slug'], [])]
    keys = ROLE_KEYS.get(role['slug'], [])
    role['asked'] = [rt for rt in routes if any(k in rt['whom'] for k in keys)]
json.dump(roles, open(os.path.join(OUT, 'roles.json'), 'w'), ensure_ascii=False, indent=1)

# ---------- processes.json ----------
def payment_steps():
    steps = []
    for r in forms['Е3']['sheets']['Шлях платежу']:
        vals = [v for _, v in sorted(r['cells'].items(), key=lambda x: int(x[0]))]
        if len(vals) >= 7 and vals[0].isdigit():
            steps.append({'num': vals[0], 'who': vals[1], 'what': vals[2], 'inp': vals[3],
                          'out': vals[4], 'term': vals[5], 'ifnot': vals[6]})
    return steps

STOP_CONDITIONS = ['Немає договору в реєстрі договорів', 'Немає підпису технагляду на акті',
 'Немає технічної довідки за місяць', 'Роботи виконані у зупинених зонах (діє акт Г4)',
 'Роботи виконані без запиту на зміну Г1 - самовільні', 'За контрагентом діє претензія з утриманням (Г8)']

processes = [
 {'slug': 'monthly-cycle', 'icon': 'refresh', 'title': 'Місячний цикл планування і закриття',
  'lead': 'Головний ритм роботи дільниці: щодня фіксуємо факт, щотижня звіряємо графік, до 25 плануємо, до 5 здаємо, до 10 ВТВ перевіряє - після цього оплата.',
  'warn': 'Пропустив крок - зупинилися гроші.',
  'steps': [
    {'num': '1', 'day': 'до 25', 'who': 'Начальник дільниці', 'what': 'Подає у ВТВ план робіт (Б1) + графік (Б2) + потребу в матеріалах (В1)', 'ifnot': 'Місяць не фінансується, матеріали не замовляються'},
    {'num': '2', 'day': 'до 28', 'who': 'ВТВ', 'what': 'Звіряє план з проєктом, кошторисом і накопичувальною відомістю; передає потребу відділу закупівель', 'ifnot': 'Зрив поставок - відповідальність ВТВ'},
    {'num': '3', 'day': 'до 5', 'who': 'Начальник дільниці', 'what': 'Здає звітний пакет (Б3): акт з 2 підписами + табелі В5 + виконавча документація + накладні', 'ifnot': 'Один документ відсутній - пакет не прийнятий'},
    {'num': '4', 'day': 'до 10', 'who': 'ВТВ', 'what': 'Перевіряє пакет, звіряє з накопичувальною відомістю, передає технічну довідку Керівнику СЗ', 'ifnot': 'Без довідки оплата місяця не підтверджується'},
    {'num': '5', 'day': 'після', 'who': 'КСЗ + фінансовий блок', 'what': 'КСЗ затверджує акти, фінансовий блок проводить оплату за лімітами', 'ifnot': ''},
  ],
  'rhythm': {
    'daily': ['До 8:30 - людність у Telegram-чат з КСЗ (по бригадах)', 'Протягом дня - 3-5 фото ключових зон у той самий чат', 'Прораб заповнює журнал виконання робіт; водій - табель техніки (В5)'],
    'weekly': ['До 17:00 пʼятниці - план-факт графіка: «Відповідає» або письмове пояснення КП', 'До 17:00 - тижневий фотозвіт (кожна робота тижня на фото)', 'До 18:00 - табелі техніки за тиждень у ВТВ + накладні і сертифікати'],
  },
  'errors': ['План не подано до 25 - місяць не фінансується', 'Пакет неповний або без підпису - оплата не розглядається', 'Перебор без пояснення - позиція не оплачується (Г9, Г8)', 'Робота за неактуальною версією креслень - переробка за рахунок винного'],
  'docs': ['Б1','Б2','В1','Б3','В5','Е1','Е3']},
 {'slug': 'payment', 'icon': 'coins', 'title': 'Шлях платежу: 8 кроків від ініціації до оплати',
  'lead': 'Жодна гривня не йде без документального підтвердження. ВТВ - фільтр, що ловить перебори ДО того, як гроші пішли.',
  'warn': 'Платежу поза реєстром не існує.',
  'steps': [{'num': s['num'], 'day': s['term'] if s['term'] != '-' else '', 'who': s['who'], 'what': s['what'], 'ifnot': s['ifnot']} for s in payment_steps()],
  'stops': STOP_CONDITIONS,
  'errors': ['Платіж в обхід реєстру - особиста відповідальність ініціатора і виконавця', 'Підпис акта за невиконані обсяги - утримання, при повторі звільнення', '3+ повернення пакетів на місяць - розбір на нараді'],
  'docs': ['Е3','Б3','В1','В3','В5','Г1','Г4','Г8','В7']},
 {'slug': 'escalation', 'icon': 'trending-up', 'title': 'Ескалація прострочок',
  'lead': 'Запит без відповіді у нормативний строк ескалюється автоматично - нікого не треба «нагадувати особисто».',
  'warn': 'Звіт, не поданий у строк, вважається неподаним.',
  'steps': [
    {'num': '1', 'day': 'до 1 дня', 'who': 'Worksection', 'what': 'Автоматичне нагадування відповідальному', 'ifnot': ''},
    {'num': '2', 'day': '2-3 дні', 'who': 'Керівник підрозділу', 'what': 'Ескалація керівнику підрозділу порушника', 'ifnot': ''},
    {'num': '3', 'day': '4-10 днів', 'who': 'Керівник СЗ', 'what': 'Ескалація КСЗ; питання виноситься на щотижневу нараду; фіксація службовою запискою (Г9)', 'ifnot': ''},
    {'num': '4', 'day': '10+ днів', 'who': 'Генеральний директор', 'what': 'Ескалація ГД', 'ifnot': ''},
  ],
  'errors': ['Ризик поза реєстром не приймається як виправдання зриву', 'Проблема, не заявлена у щоденному зведенні, не приймається як причина відставання'],
  'docs': ['Г9','А']},
 {'slug': 'hidden-works', 'icon': 'layers', 'title': 'Приховані роботи і лабораторний контроль',
  'lead': 'Роботи, які закриваються наступними, предʼявляються технагляду ДО закриття. Без протоколу лаборанта і фотофіксації АПР не приймається.',
  'warn': 'Закрив самовільно - можливе розкриття за рахунок винного.',
  'steps': [
    {'num': '1', 'day': 'завчасно', 'who': 'Нач. дільниці', 'what': 'Викликає технагляд через Worksection ДО закриття робіт наступними', 'ifnot': 'Роботи закриті самовільно'},
    {'num': '2', 'day': 'при бетонуванні', 'who': 'Лаборант', 'what': 'Відбирає зразки при КОЖНОМУ бетонуванні; випробування на 3/7/28 добу (Г7)', 'ifnot': 'АПР без протоколу не закривається'},
    {'num': '3', 'day': 'до закриття', 'who': 'Нач. дільниці', 'what': 'Фотофіксація за чек-листом Д4 + оригінали сертифікатів на матеріали', 'ifnot': 'Без фото і сертифікатів АПР не приймається'},
    {'num': '4', 'day': 'огляд', 'who': 'Технагляд', 'what': 'Оглядає роботи, підписує АПР (Г2) і виконавчі схеми або видає припис (Г3)', 'ifnot': 'Роботи із зауваженням не закриваються до усунення'},
    {'num': '5', 'day': 'щотижня', 'who': 'Нач. дільниці', 'what': 'Передає закриті АПР з комплектом у ВТВ до виконавчої документації', 'ifnot': 'Звітний пакет місяця не буде прийнятий'},
  ],
  'errors': ['Конструкція не набрала міцності за протоколом - не приймається: підсилення або демонтаж лише через Г1', 'Недобір міцності - лаборант повідомляє НЕГАЙНО, не чекаючи 28 діб'],
  'docs': ['Г2','Г7','Д4','Г3','Г1','Е6','Е7']},
 {'slug': 'project-start', 'icon': 'flag', 'title': 'Стартовий пакет проєкту',
  'lead': 'До початку будь-яких робіт має бути сформований повний стартовий пакет із 13 позицій. Це гейт: без пакета проєкт не передається в реалізацію.',
  'warn': 'Роботи, розпочаті без пакета, вважаються самовільними - оплата не гарантується.',
  'steps': [
    {'num': '1', 'day': '', 'who': 'КСЗ → ГД', 'what': 'Паспорт проєкту: ціль, бюджет, строки, KPI, зони відповідальності, ризики', 'ifnot': ''},
    {'num': '2', 'day': '', 'who': 'Проєктна група → КСЗ', 'what': 'Містобудівні умови, ТУ на мережі, проєктна документація (генплан, АР, КР), експертиза', 'ifnot': ''},
    {'num': '3', 'day': '', 'who': 'КСЗ', 'what': 'Дозвіл на виконання будівельних робіт', 'ifnot': ''},
    {'num': '4', 'day': '', 'who': 'Кошторисник + ВТВ → ГД', 'what': 'Затверджений кошторис: локальні + обʼєктні + зведений розрахунок', 'ifnot': ''},
    {'num': '5', 'day': '', 'who': 'КП + ВТВ → КСЗ/ГД', 'what': 'Графік робіт (ГВР), графік фінансування, портфель підрядників (тендер, 3 пропозиції)', 'ifnot': ''},
    {'num': '6', 'day': '', 'who': 'Інженер з ТБ, КСЗ', 'what': 'Охорона праці + накази про призначення КП і команди проєкту', 'ifnot': ''},
  ],
  'errors': ['Гейт: без повного стартового пакета проєкт не передається в реалізацію'],
  'docs': ['Д1','Д2','В7','Г1']},
]
json.dump(processes, open(os.path.join(OUT, 'processes.json'), 'w'), ensure_ascii=False, indent=1)

print('OK: docs', len(docs), '| roles', len(roles), '| kernel chapters', len(kernel_out),
      '| checklists', len(checklists), '| calendar sections', len(cal['sections']),
      '| routes', len(routes), '| processes', len(processes))
