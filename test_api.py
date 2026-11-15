import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")
print("Key found:", bool(key), "| Model:", model)

client = genai.Client(api_key=key)
try:
    r = client.models.generate_content(model=model, contents="Say hello in 5 words")
    print("SUCCESS:", r.text)
except Exception as e:
    print("FAILED:", e)
    print("Models your key can use:")
    for m in client.models.list():
        if "generateContent" in (m.supported_actions or []):
            print("  ", m.name.replace("models/", ""))
