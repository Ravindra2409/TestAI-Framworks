import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
try:
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
    MODEL = "llama-3.3-70b-versatile"  # or "llama-3.1-8b-instant"

elif PROVIDER == "gemini":
    api_key = os.getenv("GEMINI_API_KEY") or input("Enter your Gemini API key: ")
    client = OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    MODEL = "gemini-2.0-flash"

elif PROVIDER == "ollama":
    client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
    MODEL = "llama3.1"

else:
    raise ValueError(f"Unknown provider: {PROVIDER}. Use 'openai', 'groq', 'gemini', or 'ollama'.")

print(f"✅ Client ready. Provider: {PROVIDER} | Model: {MODEL}")

# Requirement to test
requirement = "The system should allow login with valid username and password."

# Extended prompt to generate structured JSON test suite
prompt = f"""
You are a QA assistant. Generate a full test suite for the requirement below.

Requirement: "{requirement}"

Include:
1. Positive test cases (valid scenarios).
2. Negative test cases (invalid inputs, error handling).
3. Boundary test cases (edge conditions, limits).

Return the output STRICTLY in JSON format with this schema:
{{
  "test_suite": {{
    "positive": [
      {{"id": "TC001", "title": "...", "steps": ["..."], "expected_result": "..."}}
    ],
    "negative": [
      {{"id": "TC002", "title": "...", "steps": ["..."], "expected_result": "..."}}
    ],
    "boundary": [
      {{"id": "TC003", "title": "...", "steps": ["..."], "expected_result": "..."}}
    ]
  }}
}}
"""

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a QA assistant that generates structured JSON test cases."},
        {"role": "user", "content": prompt}
    ]
)

print("\n✅ Raw JSON Output:\n")
answer = response.choices[0].message.content
print(answer)

# Normalize output and strip Markdown code fences
clean_answer = answer.strip()
if clean_answer.startswith("```"):
    lines = clean_answer.splitlines()
    if len(lines) >= 3 and lines[-1].strip() == "```":
        clean_answer = "\n".join(lines[1:-1]).strip()

# Parse JSON safely
try:
    test_suite = json.loads(clean_answer)
except json.JSONDecodeError:
    import re
    match = re.search(r"(\{.*\})", clean_answer, re.DOTALL)
    if match:
        clean_answer = match.group(1)
    try:
        test_suite = json.loads(clean_answer)
    except json.JSONDecodeError as e:
        print("\n❌ Failed to parse JSON. Error:", e)
        print("\n🔧 Cleaned JSON payload:\n", clean_answer)
        raise

print("\n✅ Parsed Test Suite:\n")

# Loop through categories
for category, cases in test_suite["test_suite"].items():
    print(f"\n--- {category.upper()} TEST CASES ---")
    for case in cases:
        print(f"ID: {case['id']}")
        print(f"Title: {case['title']}")
        print("Steps:")
        for step in case['steps']:
            print(f"  - {step}")
        print(f"Expected Result: {case['expected_result']}\n")

# Save to file
with open("test_suite.json", "w", encoding="utf-8") as f:
    json.dump(test_suite, f, indent=4, ensure_ascii=False)

print("💾 Test suite saved to test_suite.json")
