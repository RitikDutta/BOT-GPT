import os

GENAI_MODEL = os.getenv("GENAI_MODEL", "gemini-2.5-flash-lite")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# later we can add more models , user preferences , etc
# this is a small file as of now but later in the production application there will be many settings in this config in produciton applicaion
# so it will be easy to manage.