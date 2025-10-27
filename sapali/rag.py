from .llm import embed_texts, chat
from .vectorstore import VectorStore
from .settings import TOP_K
def answer_query(db: VectorStore, query: str, api_key=None, model=None):
    q = embed_texts([query], api_key=api_key)[0]
    hits = db.search(q, top_k=TOP_K)
    ctx = '\n---\n'.join([t for _,t,_,_ in hits])
    msgs=[{'role':'system','content':'Bạn là trợ lý Sapali. Trả lời dựa trên tài liệu sau.'},
          {'role':'user','content':f'Tài liệu:\n{ctx}\n\nCâu hỏi: {query}'}]
    ans = chat(msgs, api_key=api_key, model=model)
    return ans, hits
