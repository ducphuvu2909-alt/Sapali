import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY','')
EMBED_MODEL = 'text-embedding-3-small'
CHAT_MODEL = os.getenv('CHAT_MODEL','gpt-4o-mini')
DB_PATH = os.getenv('DB_PATH','sapali/sapali.db')
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
TOP_K = 6
