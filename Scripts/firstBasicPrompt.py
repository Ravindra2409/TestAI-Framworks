
import os
from dotenv import load_dotenv
from openai import OpenAI


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ╔══════════════════════════════════════════════════════════════╗
# ║  PROVIDER SELECTION — Change this ONE variable to switch    ║
# ║  Options: "openai", "groq", "gemini", "ollama"              ║
# ╚══════════════════════════════════════════════════════════════╝
PROVIDER = "groq"

if PROVIDER == "openai":
    api_key = os.getenv("OPENAI_API_KEY") or input("Enter your OpenAI API key: ")
    client = OpenAI(api_key=api_key)
    MODEL = "gpt-4.1-mini"

elif PROVIDER == "groq":
    api_key = os.getenv("my_API_KEY") or input("Enter your Groq API key: ")
    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    MODEL =  "llama-3.3-70b-versatile" ##  "llama-3.1-8b-instant"  # Free, supports function calling
    

## I havent tried this
elif PROVIDER == "gemini":
    api_key = os.getenv("GEMINI_API_KEY") or input("Enter your Gemini API key: ")
    client = OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    MODEL = "gemini-2.0-flash"  # Free tier: 1500 req/day, supports function calling

## I havent tried this
elif PROVIDER == "ollama":
    # Requires: ollama installed + `ollama pull llama3.1`
    client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
    MODEL = "llama3.1"

else:
    raise ValueError(f"Unknown provider: {PROVIDER}. Use 'openai', 'groq', 'gemini', or 'ollama'.")

print(f"✅ Client ready. Provider: {PROVIDER} | Model: {MODEL}")

# 3. Define a simple prompt template
requirement = "The system should allow login with valid username and password."
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a QA assistant."},
        {"role": "user", "content": f"Generate test cases for this requirement: {requirement}"}
    ]
)

print("\n✅ Generated Test Cases:\n")
# Extract the response
answer = response.choices[0].message.content
print(answer)

prompt = f"""
You are a QA assistant. Generate a full test suite for the requirement below.

Requirement: "{requirement}"

Include:
1. Positive test cases (valid scenarios).
2. Negative test cases (invalid inputs, error handling).
3. Boundary test cases (edge conditions, limits).

Format each test case with:
- ID
- Title
- Steps
- Expected Result
"""
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a QA assistant that generates structured test cases."},
        {"role": "user", "content": prompt}
    ]
)

print("\n✅ Generated Test Suite:\n")
answer = response.choices[0].message.content
print(answer)