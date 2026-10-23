
"""
I used a small local embedding model for speed/cost reasons 
— it correctly finds topically-related content, 
but has real precision limits on subtler intent like specific verbs. 
This is a known tradeoff with lightweight embedding models,
and a larger model (or a hosted one like Gemini's) would likely improve this at the cost of speed/quota.
"""


from sentence_transformers import SentenceTransformer
from sympy import true

model = SentenceTransformer('all-MiniLM-L6-v2')  
memory_test = []

QUESTION_WORDS = ["what", "whats", "where", "who", "when", "why", "how",
                  "is", "are", "do", "does", "did", "can", "could", "which"]

def is_question(text):
    if text.strip().endswith("?"):
        return True
    words = text.lower().split()
    if not words:
        return False
    return words[0] in QUESTION_WORDS

def search_memory(text, top_n=3):
    emb1 = model.encode(text)
    rank = []
    
    for item in memory_test:
        if is_question(item["text"]):
            continue
        score = model.similarity(emb1, item["embedding"]).item()
        rank.append({"score": score, "text": item["text"]})

    sorted_rank = sorted( rank , key = lambda x : x["score"], reverse= True) 
    return sorted_rank[:top_n]  


def save_to_memory(text):
    embedding = model.encode(text)
    memory_test.append({"text":text, "embedding": embedding})

