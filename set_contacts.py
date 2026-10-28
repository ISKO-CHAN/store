#!/usr/bin/env python3
"""Смена контактов магазина во всех страницах.
Запуск:  python set_contacts.py НОМЕР_WHATSAPP ТЕЛЕГРАМ_НИК "ТЕЛЕФОН ДЛЯ ПОКАЗА"
Пример:  python set_contacts.py 996700123456 my_shop "+996 700 12-34-56"
НОМЕР_WHATSAPP: международный формат без плюса и пробелов. ТЕЛЕГРАМ_НИК: без @."""
import re, sys
from pathlib import Path
if len(sys.argv) != 4: sys.exit(__doc__)
wa, tg, ph = sys.argv[1].lstrip('+'), sys.argv[2].lstrip('@'), sys.argv[3]
if not re.fullmatch(r'\d{9,15}', wa): sys.exit('Номер WhatsApp: только цифры, например 996700123456')
new = "{wa:'%s',tg:'%s',phone:'%s'}" % (wa, tg, ph.replace("'", ""))
pat = re.compile(r"\{wa:'[^']*',tg:'[^']*',phone:'[^']*'\}")
n = 0
for f in Path(__file__).parent.joinpath('static').glob('*.*'):
    if f.suffix not in ('.html', '.js'): continue
    t = f.read_text(encoding='utf-8'); t2, k = pat.subn(new, t)
    if k: f.write_text(t2, encoding='utf-8'); n += k; print(f.name, k)
print('Готово, замен:', n)
