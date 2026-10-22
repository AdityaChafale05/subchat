import os
import json
import httpx
from dotenv import load_dotenv
from rag_pipeline import save_to_memory , search_memory

load_dotenv()
API_KEY = os.getenv("api_groq")
MEMORY_FILE = "main_memory.json"

# --- Load main chat memory ---
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        try:
            conversation1 = json.load(f)
            print(f"Loaded {len(conversation1)} past messages from '{MEMORY_FILE}'.")
        except json.JSONDecodeError:
            print("Memory file was corrupted/empty. Starting fresh.")
            conversation1 = []
else:
    print("No previous memory found. Starting fresh conversation.")
    conversation1 = []

rebuilt = 0
for msg in conversation1:
    save_to_memory(msg["content"])
    rebuilt += 1
print(f"Rebuilt {rebuilt} messages into searchable memory.")
    
    


def ask_groq(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": messages,
        "max_tokens": 250
    }
    try:
        response = httpx.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            reply = result["choices"][0]["message"]["content"]
            tokens = result["usage"]["total_tokens"]
            return reply, tokens
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return None, None
    except Exception as e:
        print(f"Network/Request Error: {e}")
        return None, None


def save_memory(conversation):
    with open(MEMORY_FILE, "w") as f:
        json.dump(conversation, f, indent=2)


def ask_subchat(question):
    top_matches = search_memory(question, top_n=3)
    
    print(f"[DEBUG] top_matches = {top_matches}") 
    history_text = ""
    for item in top_matches:
        history_text += f"{item['text']}\n"

    conversation2 = [
        {"role": "user", "content": f"Background:\n{history_text}\nQuestion: {question}"}
    ]
    print(f"[DEBUG] conversation2 = {conversation2}") 
    reply, tokens = ask_groq(conversation2)
    return reply, tokens


# --- Main Loop ---
print("\n--- Chat (type 'sub' for sub-chat, 'exit' to quit) ---")

while True:
    user_input = input("\n ヾ(⌐■_■)ノ♪ You: ").strip()
    if not user_input:
        continue
    if user_input.lower() == 'exit':
        print("Goodbye!")
        break

    elif user_input.lower() == 'sub':
        print("Entered sub-chat. Type 'exit' to return to main chat.")
        while True:
            sub_question = input("Sub-chat: ")
            if sub_question.lower() == 'exit':
                print("Returning to main chat.")
                break
            reply, tokens = ask_subchat(sub_question)
            if reply:
                print(f"Sub-chat .☘︎ ݁˖ : {reply} (Tokens: {tokens})")
            else:
                print("Sub-chat request failed.")
        continue

    conversation1.append({"role": "user", "content": user_input})
    
    
    reply, usage = ask_groq(conversation1)
    if reply:
        print(f"\n ✧(ↀ_ↀ)  Assistant: {reply}")
        try:
            save_to_memory(user_input)
        except Exception as e:
            print(f"Memory warning: could not save user message: {e}")

        conversation1.append({"role": "assistant", "content": reply})
        try:
            save_to_memory(reply)
        except Exception as e:
            print(f"Memory warning: could not save assistant reply: {e}")

        save_memory(conversation1)
    else:
        conversation1.pop()
        print("\nFailed to get response. Message not saved.")