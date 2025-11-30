from dotenv import load_dotenv
load_dotenv()
import os
print("Loaded OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

from app import create_app

app = create_app() 

if __name__ == "__main__":
    app.run(debug=True)