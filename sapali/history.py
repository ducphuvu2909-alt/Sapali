import json
def export_json(db, session:str)->str:
    rows = db.export_chat(session)
    return json.dumps([{'role':r,'content':c,'ts':ts} for r,c,ts in rows], ensure_ascii=False, indent=2)
