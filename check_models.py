from google import genai
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")
print([m.name for m in client.models.list()])
