#!/usr/bin/env python3
"""НоутМаркет: сайт + SQL-база (SQLite) + API. Только стандартная библиотека Python 3.8+."""
import hmac, json, mimetypes, os, sqlite3, threading, time, urllib.request
from datetime import datetime
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).parent
DB = ROOT / 'shop.db'
STATIC = ROOT / 'static'
PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')   # поменяйте!
PUB = ("SELECT id, brand, category AS cat, name, cpu, ram_gb AS ram, ssd_gb AS ssd, screen AS scr, gpu, "
       "price_kgs AS price, photo_url AS photo, in_stock AS qty FROM v_catalog ORDER BY id")
COLS = {'name': 'name', 'cpu': 'cpu', 'ram': 'ram_gb', 'ssd': 'ssd_gb', 'scr': 'screen', 'gpu': 'gpu', 'price': 'price_kgs', 'photo': 'photo_url'}
STATUSES = ('new', 'paid', 'shipped', 'done', 'cancelled')


REVIEWS = ("CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,"
           " author TEXT NOT NULL, rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5), text TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')));")


def init():
    c = sqlite3.connect(DB)
    if not c.execute("SELECT 1 FROM sqlite_master WHERE name='products'").fetchone():
        c.executescript((ROOT / 'laptop_store.sql').read_text(encoding='utf-8'))
    c.executescript(REVIEWS); c.commit(); c.close()


def add_review(c, d):
    a = str(d.get('author', '')).strip()[:50]; t = str(d.get('text', '')).strip()[:500]; r = int(d.get('rating', 0))
    if not a or len(t) < 3 or not 1 <= r <= 5: raise ValueError('Укажите имя, оценку 1-5 и текст отзыва')
    if not c.execute('SELECT 1 FROM products WHERE id=?', (int(d['product_id']),)).fetchone(): raise ValueError('Товар не найден')
    c.execute('INSERT INTO reviews(product_id,author,rating,text) VALUES(?,?,?,?)', (int(d['product_id']), a, r, t))


def reviews_list(pid):
    c = db(); r = [dict(x) for x in c.execute('SELECT author, rating, text, created_at FROM reviews WHERE product_id=? ORDER BY id DESC LIMIT 30', (pid,))]; c.close(); return r


def notify(oid):
    """Сообщение о новом заказе в Telegram (если заданы TG_TOKEN и TG_CHAT)."""
    tok, chat = os.environ.get('TG_TOKEN'), os.environ.get('TG_CHAT')
    if not tok or not chat: return
    try:
        o = next(x for x in admin_orders() if x['id'] == oid)
        txt = f"Новый заказ №{oid}\n{o['full_name']} {o['phone']}\n" + '\n'.join(f"{i['name']} x{i['qty']}" for i in o['items']) + f"\nИтого: {o['total_kgs']} сом"
        urllib.request.urlopen(urllib.request.Request(f'https://api.telegram.org/bot{tok}/sendMessage', json.dumps({'chat_id': chat, 'text': txt}).encode(), {'Content-Type': 'application/json'}), timeout=10)
    except Exception as e: print('Telegram:', e)


def stats():
    c = db()
    r = {'orders': [dict(x) for x in c.execute("SELECT status, COUNT(*) n, COALESCE(SUM(total_kgs),0) s FROM orders GROUP BY status")],
         'revenue': c.execute("SELECT COALESCE(SUM(total_kgs),0) FROM orders WHERE status!='cancelled'").fetchone()[0],
         'top': [dict(x) for x in c.execute("SELECT p.name, SUM(i.qty) q FROM order_items i JOIN products p ON p.id=i.product_id JOIN orders o ON o.id=i.order_id WHERE o.status!='cancelled' GROUP BY p.id ORDER BY q DESC LIMIT 5")],
         'low': [dict(x) for x in c.execute("SELECT name, in_stock FROM v_catalog WHERE in_stock<=3 ORDER BY in_stock LIMIT 20")]}
    c.close(); return r


def backup():
    d = ROOT / 'backups'; d.mkdir(exist_ok=True)
    f = d / ('shop_%s.db' % datetime.now().strftime('%Y%m%d_%H%M%S'))
    a = sqlite3.connect(DB); b = sqlite3.connect(f); a.backup(b); b.close(); a.close()
    for o in sorted(d.glob('shop_*.db'))[:-10]: o.unlink()
    return f.name


def daily_backup():
    while True:
        time.sleep(86400); backup()


def db():
    c = sqlite3.connect(DB, isolation_level=None)   # транзакциями управляем сами
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c


def tx(fn, *a):
    c = db()
    try:
        c.execute('BEGIN IMMEDIATE')
        r = fn(c, *a)
        c.execute('COMMIT')
        return r
    except Exception:
        try: c.execute('ROLLBACK')
        except sqlite3.Error: pass
        raise
    finally:
        c.close()


def named(c, table, name):
    r = c.execute(f'SELECT id FROM {table} WHERE name=?', (name,)).fetchone()
    return r['id'] if r else c.execute(f'INSERT INTO {table}(name) VALUES(?)', (name,)).lastrowid


def upsert_product(c, d, pid=None):
    """Создаёт или обновляет товар. d: brand, cat, name, cpu, ram, ssd, scr, gpu, price, photo, stock{store:qty} или qty."""
    pid = int(pid or d.get('id') or 0) or None
    exists = pid and c.execute('SELECT 1 FROM products WHERE id=?', (pid,)).fetchone()
    if not exists:
        for k in ('brand', 'cat', 'name', 'price'):
            if d.get(k) in (None, ''): raise ValueError('Нужно поле: ' + k)
        pid = pid or c.execute('SELECT COALESCE(MAX(id),0)+1 FROM products').fetchone()[0]
        c.execute('INSERT INTO products(id,sku,brand_id,category_id,name,price_kgs) VALUES(?,?,?,?,?,?)',
                  (pid, 'NB-%03d' % pid, named(c, 'brands', d['brand']), named(c, 'categories', d['cat']), d['name'], int(d['price'])))
    for k, col in COLS.items():
        if k in d:
            v = int(d[k]) if k in ('ram', 'ssd', 'price') else d[k]
            if k == 'price' and v < 0: raise ValueError('Цена не может быть отрицательной')
            c.execute(f'UPDATE products SET {col}=? WHERE id=?', (v or None if k == 'photo' else v, pid))
    if d.get('brand'): c.execute('UPDATE products SET brand_id=? WHERE id=?', (named(c, 'brands', d['brand']), pid))
    if d.get('cat'): c.execute('UPDATE products SET category_id=? WHERE id=?', (named(c, 'categories', d['cat']), pid))
    stock = d.get('stock')
    if stock is None and d.get('qty') not in (None, ''):
        q = int(d['qty']); a = (q + 1) // 2; stock = {1: a, 2: q - a}
    for sid, q in (stock or {}).items():
        if int(q) < 0: raise ValueError('Остаток не может быть отрицательным')
        c.execute('INSERT INTO stock(product_id,store_id,qty) VALUES(?,?,?) ON CONFLICT(product_id,store_id) DO UPDATE SET qty=excluded.qty',
                  (pid, int(sid), int(q)))
    return pid


def create_order(c, d):
    name = str(d.get('name', '')).strip()[:100]; phone = str(d.get('phone', '')).strip()[:30]
    want = {}
    for it in d.get('items') or []:
        want[int(it['id'])] = want.get(int(it['id']), 0) + int(it['qty'])
    if not name or len(phone) < 7 or not want: raise ValueError('Укажите имя, телефон и товары')
    cu = c.execute('SELECT id FROM customers WHERE phone=?', (phone,)).fetchone()
    cid = cu['id'] if cu else c.execute('INSERT INTO customers(full_name,phone) VALUES(?,?)', (name, phone)).lastrowid
    oid = c.execute('INSERT INTO orders(customer_id) VALUES(?)', (cid,)).lastrowid
    total = 0
    for pid, q in want.items():
        if q < 1: raise ValueError('Неверное количество')
        p = c.execute('SELECT name, price_kgs FROM products WHERE id=?', (pid,)).fetchone()
        if not p: raise ValueError('Товар не найден')
        need = q
        for s in c.execute('SELECT store_id, qty FROM stock WHERE product_id=? ORDER BY store_id', (pid,)).fetchall():
            t = min(need, s['qty'])
            if t:
                c.execute('UPDATE stock SET qty=qty-? WHERE product_id=? AND store_id=?', (t, pid, s['store_id'])); need -= t
        if need: raise ValueError('Недостаточно на складе: ' + p['name'])
        c.execute('INSERT INTO order_items(order_id,product_id,qty,price_kgs) VALUES(?,?,?,?)', (oid, pid, q, p['price_kgs']))
        total += q * p['price_kgs']
    c.execute('UPDATE orders SET total_kgs=? WHERE id=?', (total, oid))
    return oid


def set_status(c, oid, st):
    if st not in STATUSES: raise ValueError('Неверный статус')
    o = c.execute('SELECT status FROM orders WHERE id=?', (oid,)).fetchone()
    if not o: raise ValueError('Заказ не найден')
    if st == 'cancelled' and o['status'] != 'cancelled':       # вернуть товар на склад
        for i in c.execute('SELECT product_id, qty FROM order_items WHERE order_id=?', (oid,)).fetchall():
            c.execute('INSERT INTO stock(product_id,store_id,qty) VALUES(?,1,?) ON CONFLICT(product_id,store_id) DO UPDATE SET qty=qty+excluded.qty', (i['product_id'], i['qty']))
    c.execute('UPDATE orders SET status=? WHERE id=?', (st, oid))


def delete_product(c, pid):
    if c.execute('SELECT 1 FROM order_items WHERE product_id=?', (pid,)).fetchone():
        raise ValueError('Товар есть в заказах: удалить нельзя, поставьте остаток 0')
    c.execute('DELETE FROM stock WHERE product_id=?', (pid,)); c.execute('DELETE FROM products WHERE id=?', (pid,))


def admin_products():
    c = db()
    stores = [dict(x) for x in c.execute('SELECT id, name FROM stores ORDER BY id')]
    ps = [dict(x) for x in c.execute(PUB)]
    sk = {}
    for r in c.execute('SELECT product_id, store_id, qty FROM stock'): sk.setdefault(r['product_id'], {})[r['store_id']] = r['qty']
    for p in ps: p['stock'] = sk.get(p['id'], {})
    c.close()
    return {'stores': stores, 'products': ps}


def admin_orders():
    c = db()
    os_ = [dict(x) for x in c.execute('SELECT o.id, o.created_at, o.status, o.total_kgs, cu.full_name, cu.phone FROM orders o JOIN customers cu ON cu.id=o.customer_id ORDER BY o.id DESC LIMIT 200')]
    for o in os_:
        o['items'] = [dict(x) for x in c.execute('SELECT p.name, i.qty, i.price_kgs FROM order_items i JOIN products p ON p.id=i.product_id WHERE i.order_id=?', (o['id'],))]
    c.close()
    return os_


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def out(self, code, obj=None, raw=None, ctype='application/json; charset=utf-8'):
        b = raw if raw is not None else json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Content-Length', str(len(b)))
        self.send_header('Cache-Control', 'no-store' if raw is None else 'no-cache'); self.end_headers(); self.wfile.write(b)

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        return json.loads(self.rfile.read(n) or b'{}')

    def go(self, m):
        p = urlparse(self.path).path
        try:
            if p.startswith('/api/'): return self.api(m, p)
            if m != 'GET': return self.out(405, {'error': 'method'})
            f = {'/': 'index.html', '/catalog': 'catalog.html', '/pc': 'pc.html', '/admin': 'admin.html'}.get(p) or p.lstrip('/')
            fp = (STATIC / f).resolve()
            if STATIC.resolve() not in fp.parents or not fp.is_file(): return self.out(404, {'error': 'not found'})
            ct = (mimetypes.guess_type(fp.name)[0] or 'application/octet-stream') + ('; charset=utf-8' if fp.suffix in ('.html', '.js', '.css') else '')
            self.out(200, raw=fp.read_bytes(), ctype=ct)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            self.out(400, {'error': str(e) or 'Неверные данные'})
        except Exception as e:
            print('ERROR', e); self.out(500, {'error': 'Ошибка сервера'})

    def api(self, m, p):
        if p == '/api/products' and m == 'GET':
            c = db(); r = [dict(x) for x in c.execute(PUB)]; c.close(); return self.out(200, r)
        if p == '/api/orders' and m == 'POST':
            oid = tx(create_order, self.body()); threading.Thread(target=notify, args=(oid,), daemon=True).start()
            return self.out(201, {'id': oid})
        if p == '/api/reviews' and m == 'GET': return self.out(200, reviews_list(int(parse_qs(urlparse(self.path).query).get('product', ['0'])[0])))
        if p == '/api/reviews' and m == 'POST': tx(add_review, self.body()); return self.out(201, {'ok': 1})
        if not p.startswith('/api/admin/'): return self.out(404, {'error': 'not found'})
        if not hmac.compare_digest(self.headers.get('X-Admin', '').encode(), PASSWORD.encode()):
            return self.out(401, {'error': 'Неверный пароль'})
        q = p[len('/api/admin/'):].split('/')
        if q == ['products'] and m == 'GET': return self.out(200, admin_products())
        if q == ['products'] and m == 'POST': return self.out(201, {'id': tx(upsert_product, self.body())})
        if q[0] == 'products' and len(q) == 2 and m == 'PUT': return self.out(200, {'id': tx(upsert_product, self.body(), int(q[1]))})
        if q[0] == 'products' and len(q) == 2 and m == 'DELETE': tx(delete_product, int(q[1])); return self.out(200, {'ok': 1})
        if q == ['orders'] and m == 'GET': return self.out(200, admin_orders())
        if q == ['stats'] and m == 'GET': return self.out(200, stats())
        if q == ['backup'] and m == 'POST': return self.out(200, {'file': backup()})
        if q[0] == 'orders' and len(q) == 3 and q[2] == 'status' and m == 'POST':
            tx(set_status, int(q[1]), self.body().get('status')); return self.out(200, {'ok': 1})
        self.out(404, {'error': 'not found'})

    do_GET = lambda s: s.go('GET')
    do_POST = lambda s: s.go('POST')
    do_PUT = lambda s: s.go('PUT')
    do_DELETE = lambda s: s.go('DELETE')


if __name__ == '__main__':
    init(); backup(); threading.Thread(target=daily_backup, daemon=True).start()
    port = int(os.environ.get('PORT', 8000))
    if PASSWORD == 'admin123': print('ВНИМАНИЕ: пароль админки по умолчанию. Задайте ADMIN_PASSWORD.')
    print(f'Магазин: http://localhost:{port}   Админка: http://localhost:{port}/admin')
    ThreadingHTTPServer(('0.0.0.0', port), H).serve_forever()
