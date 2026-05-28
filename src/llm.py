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

# --- Models to try in order ---
# If one hits quota limit, automatically tries next one
GEMINI_MODELS = [
    "gemini-2.0-flash-lite",      # Best free quota
    "gemini-2.5-flash-lite",      # Second choice
    "gemini-flash-lite-latest",   # Always latest lite
    "gemini-2.0-flash",           # Fallback
    "gemini-flash-latest",        # Last resort
]

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

def call_gemini_with_fallback(
    full_prompt: str,
    max_tokens: int,
    temperature: float,
    preferred_model: str = None
) -> str:
    """
    Tries multiple Gemini models in order.
    If one fails with quota error, automatically tries next.
    """
    # Build model list — preferred model first if specified
    models_to_try = []
    if preferred_model:
        models_to_try.append(preferred_model)
    for m in GEMINI_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    safety_settings = [
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

    last_error = None

    for model in models_to_try:
        try:
            print(f"Trying model: {model}")
            response = gemini_client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    safety_settings=safety_settings
                )
            )

            if not response.text:
                print(f"Model {model} returned empty response, trying next...")
                continue

            print(f"Success with model: {model}")
            return response.text.strip().replace("```", "").strip()

        except Exception as e:
            error_str = str(e)
            last_error = error_str

            # Quota exceeded — try next model
            if "429" in error_str:
                print(f"Model {model} quota exceeded, trying next...")
                continue

            # Model not found — try next model
            elif "404" in error_str:
                print(f"Model {model} not found, trying next...")
                continue

            # Service unavailable — try next model
            elif "503" in error_str:
                print(f"Model {model} unavailable, trying next...")
                continue

            # Unknown error — try next model
            else:
                print(f"Model {model} error: {e}, trying next...")
                continue

    # All models failed
    return f"Gemini LLM error: All models exhausted. Last error: {last_error}"

def call_llm(
    prompt: str,
    system_prompt: str = None,
    provider: str = "google",
    model: str = None,
    max_tokens: int = 3000,
    temperature: float = 0.2
) -> str:
    """
    Calls the specified LLM provider with the given prompt.
    Automatically falls back to next model on quota errors.
    """
    final_system_prompt = system_prompt or "You are a helpful senior software engineer."

    if provider == "google":
        if not gemini_client:
            return "LLM Error: Gemini client is not configured. Check GOOGLE_API_KEY."

        full_prompt = f"System: {final_system_prompt}\n\nUser: {prompt}"

        return call_gemini_with_fallback(
            full_prompt=full_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            preferred_model=model
        )

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
