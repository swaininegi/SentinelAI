import sqlite3, json, datetime
DB_PATH='data/sentinelai.db'

def init_db():
    con=sqlite3.connect(DB_PATH); cur=con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS scans(id INTEGER PRIMARY KEY AUTOINCREMENT, scan_type TEXT, input_text TEXT, score INTEGER, level TEXT, explanation TEXT, created_at TEXT)''')
    con.commit(); con.close()

def log_scan(scan_type,input_text,score,level,explanation):
    init_db(); con=sqlite3.connect(DB_PATH); cur=con.cursor()
    cur.execute('INSERT INTO scans(scan_type,input_text,score,level,explanation,created_at) VALUES(?,?,?,?,?,?)',(scan_type,input_text[:1000],int(score),level,explanation,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    con.commit(); con.close()

def get_scans(limit=200):
    init_db(); con=sqlite3.connect(DB_PATH)
    rows=con.execute('SELECT scan_type,input_text,score,level,explanation,created_at FROM scans ORDER BY id DESC LIMIT ?', (limit,)).fetchall(); con.close()
    return rows

def stats():
    rows=get_scans(10000)
    total=len(rows); threats=sum(1 for r in rows if r[2]>=60); critical=sum(1 for r in rows if r[2]>=85)
    return {'total':total,'threats':threats,'safe':total-threats,'critical':critical}
