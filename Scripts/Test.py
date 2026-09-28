import os
from openai import OpenAI

client = OpenAI()
api_key = "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"
client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
MODEL =  "llama-3.3-70b-versatile" ##  "llama-3.1-8b-instant"  # Free, supports function calling

response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role":"user","content":"What is the capital of France?"}]
)
print(response.choices[0].message.content)
