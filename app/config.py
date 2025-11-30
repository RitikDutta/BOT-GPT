import os

GENAI_MODEL = os.getenv("GENAI_MODEL", "gemini-2.5-flash-lite")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "bot_gpt_test")

# openai embed config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

# pinecone config
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_HOST = os.getenv("PINECONE_INDEX_HOST")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "bot-gpt")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "bot-gpt")

# later we can add more models , user preferences , etc
# this is a small file as of now but later in the production application there will be many settings in this config in produciton applicaion
# so it will be easy to manage.