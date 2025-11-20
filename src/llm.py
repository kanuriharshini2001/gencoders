# src/llm.py
from dotenv import load_dotenv
import os
import google.generativeai as genai
from openai import OpenAI, APIError

load_dotenv()

# --- Google Gemini Configuration (Primary) ---
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")  # <-- Variable is defined here
gemini_client = None
if not GOOGLE_KEY:  # <-- This line is now fixed
    print("Warning: GOOGLE_API_KEY not found in .env. Gemini calls will fail.")
else:
    try:
        genai.configure(api_key=GOOGLE_KEY)
        gemini_client = genai.GenerativeModel("gemini-flash-latest") 
        print("Gemini client configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini client: {e}")

# --- OpenAI Configuration (Fallback) ---
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai_client = None
if not OPENAI_KEY:
    print("Warning: OPENAI_API_KEY not found in .env. OpenAI calls will fail.")
else:
    openai_client = OpenAI(api_key=OPENAI_KEY)
    print("OpenAI client configured.")


def call_llm(
    prompt: str, 
    system_prompt: str = None,
    provider: str = "google",
    model: str = None,
    max_tokens: int = 2048,
    temperature: float = 0.2
) -> str:
    
    """
    Calls the specified LLM provider with the given prompt.
    """
    
    final_system_prompt = system_prompt or "You are a helpful senior software engineer."

    if provider == "google":
        if not gemini_client:
            return "LLM Error: Gemini client is not configured. Check GOOGLE_API_KEY."
        
        model_instance = genai.GenerativeModel(model) if model else gemini_client
        
        full_prompt = f"System: {final_system_prompt}\n\nUser: {prompt}"
        
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature
        )

        # Define permissive safety settings to prevent false positives
        safety_settings = {
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
        }

        try:
            response = model_instance.generate_content(
                full_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            # Add a check for a valid response before accessing .text
            if not response.parts:
                return "Gemini LLM Error: Response was blocked by API (safety or other)."
                
            return response.text.strip().replace("```python", "").replace("```", "").strip()
        except ValueError as e:
            # Catch the "Invalid operation" error more gracefully
            return f"Gemini LLM error: Response was empty or blocked. Finish Reason: {e}"
        except Exception as e:
            return f"Gemini LLM error: {e}"

    elif provider == "openai":
        if not openai_client:
            return "LLM Error: OpenAI client is not configured. Check OPENAI_API_KEY."
        
        current_model = model or "gpt-4o-mini"
        
        try:
            resp = openai_client.chat.completions.create(
                model=current_model,
                messages=[
                    {"role": "system", "content": final_system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content.strip()
        except APIError as e:
            return f"OpenAI API error: {e}"
        except Exception as e:
            return f"OpenAI LLM error: {e}"
    
    else:
        return f"LLM Error: Unknown provider '{provider}'. Use 'google' or 'openai'."