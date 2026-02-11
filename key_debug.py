import os
from dotenv import load_dotenv

load_dotenv(override=True)

key = os.getenv("GEMINI_API_KEY")

print("KEY FROM ENV =", key)
print("KEY LENGTH =", len(key) if key else "NONE")
