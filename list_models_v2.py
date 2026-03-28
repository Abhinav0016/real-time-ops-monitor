import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("No GOOGLE_API_KEY found.")
else:
    genai.configure(api_key=api_key)
    try:
        print("Filtering for flash/pro models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower() or 'pro' in m.name.lower():
                    print(f"- {m.name}")
    except Exception as e:
        print(f"Error: {e}")
