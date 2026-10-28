#!/usr/bin/env python3
"""Управление базой из консоли.
  python manage.py list [текст]            список товаров с ценой и остатками
  python manage.py price ID СУММА          изменить цену (сом)
  python manage.py stock ID МАГАЗИН КОЛ    задать остаток в магазине (1 или 2)
  python manage.py import products.csv     загрузить каталог из CSV (экспорт из Access)
  python manage.py sql "SELECT ..."        любой SQL-запрос"""
import csv, sys
from server import db, init, tx, upsert_product, PUB

def main(a):
    init()
    if not a: return print(__doc__)
    cmd = a[0]
    if cmd == 'list':
        t = (a[1] if len(a) > 1 else '').lower(); c = db()
        for r in c.execute(PUB):
            if t in (r['brand'] + ' ' + r['name']).lower(): print(f"{r['id']:>3}  {r['brand']:<8} {r['name']:<26} {r['price']:>8} сом   остаток: {r['qty']}")
    elif cmd == 'price': tx(lambda c: upsert_product(c, {'price': int(a[2])}, int(a[1]))); print('Готово')
    elif cmd == 'stock': tx(lambda c: upsert_product(c, {'stock': {int(a[2]): int(a[3])}}, int(a[1]))); print('Готово')
    elif cmd == 'import':
        with open(a[1], encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f, delimiter=';'))
        tx(lambda c: [upsert_product(c, {k.strip().lower(): v for k, v in r.items()}) for r in rows]); print('Загружено:', len(rows))
    elif cmd == 'sql':
        c = db()
        for r in c.execute(a[1]): print(tuple(r))
    else: print(__doc__)

main(sys.argv[1:])
