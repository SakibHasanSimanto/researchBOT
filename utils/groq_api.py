import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

import re

def split_thoughts(output: str):
    """
    Extract reasoning enclosed in <think>...</think> tags if present,
    return tuple (reasoning, rest_of_output)
    """
    match = re.search(r"<think>(.*?)</think>", output, flags=re.DOTALL)
    if match:
        thinking = match.group(1).strip()
        final_output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL).strip()
        return thinking, final_output
    return None, output


def call_groq_model(prompt: str, model: str) -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found in environment variables.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a professional academic reviewer. Be concise, direct, and unbiased."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise RuntimeError(f"[GROQ API Error {response.status_code}]: {response.text}")
