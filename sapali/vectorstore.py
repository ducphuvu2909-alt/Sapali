import sqlite3, json, math, time
class VectorStore:
    def __init__(self, path): self.path=path; self._init()
    def _init(self):
        con=sqlite3.connect(self.path); cur=con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY AUTOINCREMENT,file_id TEXT,name TEXT,mime TEXT,modified TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS chunks(id INTEGER PRIMARY KEY AUTOINCREMENT,doc_id INTEGER,pos INTEGER,text TEXT,embedding TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS chats(id INTEGER PRIMARY KEY AUTOINCREMENT,session TEXT,role TEXT,content TEXT,ts REAL)')
        con.commit(); con.close()
    def add_document(self,file_id,name,mime,modified):
        con=sqlite3.connect(self.path); cur=con.cursor(); cur.execute('INSERT INTO documents(file_id,name,mime,modified) VALUES(?,?,?,?)',(file_id,name,mime,modified)); i=cur.lastrowid; con.commit(); con.close(); return i
    def add_chunks(self,doc_id,items):
        con=sqlite3.connect(self.path); cur=con.cursor()
        for pos,text,emb in items: cur.execute('INSERT INTO chunks(doc_id,pos,text,embedding) VALUES(?,?,?,?)',(doc_id,pos,text,json.dumps(emb)))
        con.commit(); con.close()
    def list_docs(self):
        con=sqlite3.connect(self.path); cur=con.cursor(); cur.execute('SELECT id,name,mime,modified FROM documents ORDER BY id DESC'); rows=cur.fetchall(); con.close(); return rows
    def search(self, q_emb, top_k=6):
        con=sqlite3.connect(self.path); cur=con.cursor(); cur.execute('SELECT id,doc_id,pos,text,embedding FROM chunks'); rows=cur.fetchall(); con.close()
        def cos(a,b): 
            dot=sum(x*y for x,y in zip(a,b)); na=math.sqrt(sum(x*x for x in a)); nb=math.sqrt(sum(y*y for y in b)); 
            return 0 if na==0 or nb==0 else dot/(na*nb)
        scored=[(cos(q_emb, json.loads(e)), t, d, p) for _,d,p,t,e in rows]; scored.sort(reverse=True, key=lambda x:x[0]); return scored[:top_k]
    def append_chat(self, session, role, content):
        con=sqlite3.connect(self.path); cur=con.cursor(); cur.execute('INSERT INTO chats(session,role,content,ts) VALUES(?,?,?,?)',(session,role,content,time.time())); con.commit(); con.close()
    def export_chat(self, session):
        con=sqlite3.connect(self.path); cur=con.cursor(); cur.execute('SELECT role,content,ts FROM chats WHERE session=? ORDER BY id ASC',(session,)); rows=cur.fetchall(); con.close(); return rows
