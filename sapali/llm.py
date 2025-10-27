from openai import OpenAI
from .settings import OPENAI_API_KEY, EMBED_MODEL, CHAT_MODEL
def client(api_key=None): return OpenAI(api_key=api_key or OPENAI_API_KEY)
def embed_texts(texts, api_key=None):
    cli = client(api_key); res = cli.embeddings.create(model=EMBED_MODEL, input=texts); return [d.embedding for d in res.data]
def chat(messages, api_key=None, model=None, temperature=0.2):
    cli = client(api_key); res = cli.chat.completions.create(model=model or CHAT_MODEL, messages=messages, temperature=temperature); return res.choices[0].message.content
