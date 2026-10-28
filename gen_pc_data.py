import json
RATE=87.45   # официальный курс НБКР на октябрь 2026
K=lambda usd:int(round(usd*RATE/100.0))*100
CPU={'r5_7600':('AMD Ryzen 5 7600',200),'r5_9600x':('AMD Ryzen 5 9600X',260),'i5_14600k':('Intel Core i5-14600K',290),'r7_9700x':('AMD Ryzen 7 9700X',330),'i7_14700k':('Intel Core i7-14700K',400),
 'r7_9800x3d':('AMD Ryzen 7 9800X3D',520),'cu7_265k':('Intel Core Ultra 7 265K',390),'cu9_285k':('Intel Core Ultra 9 285K',620),'r9_9900x':('AMD Ryzen 9 9900X',430),
 'r9_9950x':('AMD Ryzen 9 9950X',620),'r9_9950x3d':('AMD Ryzen 9 9950X3D',720),'tr_7960x':('AMD Threadripper 7960X, 24 ядра',1500),'tr_7970x':('AMD Threadripper 7970X, 32 ядра',2500)}
GPU={'rx9060xt':('AMD Radeon RX 9060 XT 16 ГБ',380),'rtx5060ti':('NVIDIA GeForce RTX 5060 Ti 16 ГБ',480),'rtx5070':('NVIDIA GeForce RTX 5070 12 ГБ',650),'rx9070xt':('AMD Radeon RX 9070 XT 16 ГБ',720),
 'rtx5070ti':('NVIDIA GeForce RTX 5070 Ti 16 ГБ',950),'rtx5080':('NVIDIA GeForce RTX 5080 16 ГБ',1500),'rtx5090':('NVIDIA GeForce RTX 5090 32 ГБ',4000)}
PERF={'rx9060xt':'1080p ультра, 1440p высокие','rtx5060ti':'1440p высокие','rtx5070':'1440p ультра','rx9070xt':'1440p ультра','rtx5070ti':'1440p ультра, 4K высокие','rtx5080':'4K ультра','rtx5090':'4K ультра с трассировкой, VR'}
GSZ={'rx9060xt':0,'rtx5060ti':0,'rtx5070':1,'rx9070xt':1,'rtx5070ti':1,'rtx5080':2,'rtx5090':2}
RAM={'32':('32 ГБ DDR5-6000 (2×16)',200),'64':('64 ГБ DDR5-6000 (2×32)',400),'128':('128 ГБ DDR5 (4×32)',800),'256':('256 ГБ DDR5 ECC (8×32)',1900)}
SSD={'1':('SSD NVMe Gen4 1 ТБ',100),'2':('SSD NVMe Gen4 2 ТБ',170),'4':('SSD NVMe Gen4 4 ТБ',340)}
MB={'b650':('Материнская плата B650, AM5',150),'b850':('Материнская плата B850, AM5, Wi-Fi 7',200),'x870e':('Материнская плата X870E, AM5, Wi-Fi 7',370),'z790':('Материнская плата Z790, LGA1700',220),
 'z890':('Материнская плата Z890, LGA1851, Wi-Fi 7',300),'trx50':('Материнская плата TRX50, sTR5',750),'b850i':('Материнская плата B850 mini-ITX',260),'x870i':('Материнская плата X870 mini-ITX',400)}
PSU={'650':('Блок питания 650 Вт 80+ Gold',75),'750':('Блок питания 750 Вт 80+ Gold',100),'850':('Блок питания 850 Вт 80+ Gold',130),'1000':('Блок питания 1000 Вт 80+ Platinum',180),
 '1200':('Блок питания 1200 Вт 80+ Platinum, ATX 3.1',250),'s750':('Блок питания SFX 750 Вт 80+ Gold',140),'s850':('Блок питания SFX 850 Вт 80+ Gold',170),'s1000':('Блок питания SFX 1000 Вт 80+ Platinum',220)}
CASE={'mid':('Корпус Mid Tower, закалённое стекло',80),'white':('Корпус белый, стекло, ARGB-вентиляторы',130),'pro':('Корпус Full Glass, 3 ARGB-вентилятора',190),'ws':('Корпус для рабочих станций, шумоизоляция',250),'itx':('Корпус mini-ITX, стекло',150),'itxp':('Корпус mini-ITX Premium',180)}
COOL={'air':('Башенный кулер 120 мм',40),'air2':('Двухбашенный кулер 2×120 мм',80),'aio240':('СЖО 240 мм, ARGB',110),'aio360':('СЖО 360 мм, ARGB',170),'aio360w':('СЖО 360 мм для sTR5',220),'lp':('Низкопрофильный кулер',90),'aio240i':('СЖО 240 мм для mini-ITX',120)}
FEE={'Игровые 1440p':70,'Игровые 4K':100,'Для творчества':100,'Флагманы RTX 5090':140,'Рабочие станции':190,'Компактные':110}
STEPS=[('Сборка и установка комплектующих',.40),('Прокладка кабелей, настройка BIOS',.20),('Установка Windows, драйверов и программ',.20),('Тест под нагрузкой (стресс-тест)',.20)]
# name, cat, white, rgb, cpu, gpu, ram, [ssd], mb, psu, case, cool, use
B=[
('NM Start 9060','Игровые 1440p',0,'#ff3b30','r5_7600','rx9060xt','32',['1'],'b650','650','mid','air','Вход в современные игры, учёба и работа'),
('NM Start 5060 Ti','Игровые 1440p',1,'#22d3ee','r5_9600x','rtx5060ti','32',['1'],'b650','750','white','air','Игры в 1440p и стриминг'),
('NM Core 5060 Ti','Игровые 1440p',0,'#8b5cf6','i5_14600k','rtx5060ti','32',['1'],'z790','750','mid','air2','Игры, учёба, монтаж'),
('NM Play 5070','Игровые 1440p',0,'#34d399','r7_9700x','rtx5070','32',['2'],'b850','750','mid','air2','Игры в 1440p на ультра'),
('NM Play White 5070','Игровые 1440p',1,'#f472b6','r7_9700x','rtx5070','32',['2'],'b850','850','white','aio240','Белая сборка для игр в 1440p'),
('NM Red 9070 XT','Игровые 1440p',0,'#ef4444','r7_9700x','rx9070xt','32',['2'],'b850','850','mid','aio240','Мощная графика AMD для 1440p'),
('NM Core 5070','Игровые 1440p',0,'#60a5fa','i7_14700k','rtx5070','32',['1'],'z790','850','mid','aio240','Игры и работа с видео'),
('NM X3D 5070 Ti','Игровые 4K',0,'#22d3ee','r7_9800x3d','rtx5070ti','32',['2'],'b850','850','pro','aio240','Лучший игровой процессор и 4K'),
('NM X3D White 5070 Ti','Игровые 4K',1,'#a78bfa','r7_9800x3d','rtx5070ti','64',['2'],'x870e','1000','white','aio360','Белый флагман для игр и стриминга'),
('NM Intel 5070 Ti','Игровые 4K',0,'#38bdf8','cu7_265k','rtx5070ti','32',['2'],'z890','850','pro','aio360','Игры и тяжёлые программы'),
('NM X3D 9070 XT','Игровые 4K',0,'#fb923c','r7_9800x3d','rx9070xt','32',['2'],'b850','850','mid','aio240','4K-игры на видеокарте AMD'),
('NM Ultra 5080','Игровые 4K',0,'#22c55e','r7_9800x3d','rtx5080','32',['2'],'x870e','1000','pro','aio360','4K ультра без компромиссов'),
('NM Ultra White 5080','Игровые 4K',1,'#f0abfc','r7_9800x3d','rtx5080','64',['4'],'x870e','1000','white','aio360','Белая 4K-сборка с запасом памяти'),
('NM Intel 5080','Игровые 4K',0,'#3b82f6','cu9_285k','rtx5080','64',['2'],'z890','1000','pro','aio360','Игры 4K и многозадачность'),
('NM Creator 5080','Для творчества',0,'#f59e0b','r9_9950x','rtx5080','64',['4'],'x870e','1000','pro','aio360','Монтаж 4K/8K, 3D-рендер, ИИ'),
('NM Beast 5090','Флагманы RTX 5090',0,'#ef4444','r7_9800x3d','rtx5090','64',['4'],'x870e','1200','pro','aio360','Максимум в играх, VR и нейросетях'),
('NM Beast White 5090','Флагманы RTX 5090',1,'#e879f9','r9_9950x3d','rtx5090','128',['4'],'x870e','1200','white','aio360','Белый флагман для игр и работы'),
('NM Beast Intel 5090','Флагманы RTX 5090',0,'#2dd4bf','cu9_285k','rtx5090','64',['4'],'z890','1200','pro','aio360','Рендер, игры, нейросети'),
('NM Creator 5070 Ti','Для творчества',0,'#fbbf24','r9_9900x','rtx5070ti','64',['4'],'x870e','850','mid','aio360','Фото, видео, дизайн, 3D'),
('NM Studio Intel','Для творчества',1,'#818cf8','cu7_265k','rtx5070','64',['2'],'z890','850','white','aio240','Студия: монтаж и звук'),
('NM Pro TR 24','Рабочие станции',0,'#94a3b8','tr_7960x','rtx5080','128',['4'],'trx50','1000','ws','aio360w','Инженерные расчёты, рендер, виртуализация'),
('NM Pro TR 32','Рабочие станции',0,'#f87171','tr_7970x','rtx5090','256',['4','4'],'trx50','1200','ws','aio360w','Тяжёлый рендер, ИИ, сервер разработки'),
('NM Mini 5060 Ti','Компактные',0,'#22d3ee','r5_9600x','rtx5060ti','32',['1'],'b850i','s750','itx','lp','Малый размер для стола и гостиной'),
('NM Mini 5070','Компактные',1,'#fb7185','r7_9700x','rtx5070','32',['2'],'b850i','s850','itxp','lp','Компактный игровой ПК'),
('NM Mini X3D 5070 Ti','Компактные',0,'#a3e635','r7_9800x3d','rtx5070ti','32',['2'],'x870i','s1000','itxp','aio240i','Мини-ПК с флагманским процессором'),
]
out=[]
for i,(name,cat,white,rgb,cpu,gpu,ram,ssd,mb,psu,case,cool,use) in enumerate(B,1):
    parts=[('cpu','Процессор',CPU[cpu]),('gpu','Видеокарта',GPU[gpu]),('mb','Материнская плата',MB[mb]),('ram','Оперативная память',RAM[ram])]
    parts+=[('ssd','Накопитель',SSD[s]) for s in ssd]
    parts+=[('psu','Блок питания',PSU[psu]),('case','Корпус',CASE[case]),('cool','Охлаждение',COOL[cool])]
    pl=[{'k':k,'t':t,'n':n,'usd':u,'kgs':K(u)} for k,t,(n,u) in parts]
    fee=FEE[cat];feek=K(fee)
    steps=[{'n':n,'kgs':int(round(feek*s/100.0))*100} for n,s in STEPS]
    steps[-1]['kgs']=feek-sum(x['kgs'] for x in steps[:-1])
    total=sum(p['kgs'] for p in pl)+feek
    out.append({'id':i,'name':name,'cat':cat,'white':white,'rgb':rgb,'use':use,'perf':PERF[gpu],'gsz':GSZ[gpu],'cool':cool,'ram':int(ram),'mini':case.startswith('itx'),'ws':case=='ws',
      'parts':pl,'master':feek,'steps':steps,'total':total,'usd':round(total/RATE)})
mn=min(x['usd'] for x in out);mx=max(x['usd'] for x in out)
print(len(out),'сборок, от $%d до $%d'%(mn,mx),'; от',min(x['total'] for x in out),'до',max(x['total'] for x in out),'сом')
json.dump({'rate':RATE,'builds':out},open('pcs.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
# SQL
q=lambda s:"'"+str(s).replace("'","''")+"'"
sql=["\n-- ПК (системные блоки): курс НБКР, цены комплектующих по рынку США пересчитаны в сомы",
"CREATE TABLE IF NOT EXISTS pc_builds (id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, use_case TEXT, master_fee_kgs INTEGER NOT NULL);",
"CREATE TABLE IF NOT EXISTS pc_parts (id INTEGER PRIMARY KEY AUTOINCREMENT, build_id INTEGER NOT NULL REFERENCES pc_builds(id) ON DELETE CASCADE, kind TEXT NOT NULL, name TEXT NOT NULL, price_usd INTEGER NOT NULL, price_kgs INTEGER NOT NULL);",
"CREATE VIEW IF NOT EXISTS v_pc AS SELECT b.id, b.name, b.category, b.master_fee_kgs, SUM(p.price_kgs) AS parts_kgs, SUM(p.price_kgs)+b.master_fee_kgs AS total_kgs FROM pc_builds b JOIN pc_parts p ON p.build_id=b.id GROUP BY b.id;"]
sql.append("INSERT OR IGNORE INTO pc_builds(id,name,category,use_case,master_fee_kgs) VALUES\n"+",\n".join("(%d,%s,%s,%s,%d)"%(b['id'],q(b['name']),q(b['cat']),q(b['use']),b['master']) for b in out)+";")
rows=[]
for b in out:
    for p in b['parts']:rows.append("(%d,%s,%s,%d,%d)"%(b['id'],q(p['k']),q(p['n']),p['usd'],p['kgs']))
sql.append("INSERT INTO pc_parts(build_id,kind,name,price_usd,price_kgs) SELECT * FROM (VALUES\n"+",\n".join(rows)+")\nWHERE NOT EXISTS (SELECT 1 FROM pc_parts);")
open('pc.sql','w',encoding='utf-8').write("\n".join(sql)+"\n")
