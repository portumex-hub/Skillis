"""
Free streaming chatbot using Groq (Llama 3.3 70B).
Get your free API key at: https://console.groq.com
"""

import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = "You are a helpful assistant. Be concise and clear."

def chat(history: list[dict]) -> str:
    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        stream=True,
    )
    response = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        print(delta, end="", flush=True)
        response += delta
    print()
    return response


def main():
    print("🤖 Free AI Chatbot (Groq + Llama 3.3 70B)")
    print("   Type 'exit' to quit\n")

    history = []
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit", "bye"):
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})
        print("Assistant: ", end="")
        reply = chat(history)
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
