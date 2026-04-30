import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

conversation_history = [
    {
        "role": "system",
        "content": (
            "You are Atlas, a smart, friendly personal AI assistant running on Android. "
            "Keep replies short, clear, and helpful. "
            "When confirming actions like opening apps or changing settings, be brief and friendly."
        )
    }
]

def ask_ai(prompt):
    conversation_history.append({"role": "user", "content": prompt})
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation_history,
            max_tokens=300
        )
        reply = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"AI Error: {str(e)}"

def clear_history():
    global conversation_history
    conversation_history = [conversation_history[0]]