# src/llm.py
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from openai import OpenAI, APIError

load_dotenv()

# --- Google Gemini Configuration (Primary) ---
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
gemini_client = None

if not GOOGLE_KEY:
    print("Error: GOOGLE_API_KEY not found in .env. Gemini calls will fail.")
else:
    try:
        gemini_client = genai.Client(api_key=GOOGLE_KEY)
    except Exception as e:
        print(f"Error configuring Gemini client: {e}")

# --- OpenAI Configuration (Lazy Load) ---
openai_client = None

def get_openai_client():
    """Helper to load OpenAI client only when needed."""
    global openai_client
    if openai_client:
        return openai_client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    openai_client = OpenAI(api_key=api_key)
    return openai_client

def call_llm(
    prompt: str,
    system_prompt: str = None,
    provider: str = "google",
    model: str = None,
    max_tokens: int = 1024,
    temperature: float = 0.2
) -> str:
    """
    Calls the specified LLM provider with the given prompt.
    """
    final_system_prompt = system_prompt or "You are a helpful senior software engineer."

    if provider == "google":
        if not gemini_client:
            return "LLM Error: Gemini client is not configured. Check GOOGLE_API_KEY."

        # ✅ Fixed model name — 1500 requests/day free tier
        current_model = model or "gemini-2.5-flash"

        full_prompt = f"System: {final_system_prompt}\n\nUser: {prompt}"

        try:
            response = gemini_client.models.generate_content(
                model=current_model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    safety_settings=[
                        types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT",
                            threshold="BLOCK_NONE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH",
                            threshold="BLOCK_NONE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="BLOCK_NONE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="BLOCK_NONE"
                        ),
                    ]
                )
            )

            if not response.text:
                return "Gemini LLM Error: Response was blocked by API."

            return response.text.strip().replace("```python", "").replace("```", "").strip()

        except Exception as e:
            return f"Gemini LLM error: {e}"

    elif provider == "openai":
        client = get_openai_client()
        if not client:
            return "LLM Error: OpenAI client is not configured. Check OPENAI_API_KEY."

        current_model = model or "gpt-4o-mini"

        try:
            resp = client.chat.completions.create(
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
