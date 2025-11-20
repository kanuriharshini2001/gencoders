import google.generativeai as genai
import os
from dotenv import load_dotenv

try:
    # Load .env file (same as your other scripts)
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env file.")
    else:
        genai.configure(api_key=api_key)
        
        print("--- Checking for available models ---")
        
        found_models = False
        for m in genai.list_models():
            # This check is crucial!
            # It only shows models that support the 'generateContent' method.
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model: {m.name}")
                found_models = True
        
        if not found_models:
            print("No models found that support 'generateContent'.")
        
        print("-------------------------------------")

except Exception as e:
    print(f"An error occurred: {e}")