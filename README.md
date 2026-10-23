
# subchat

**Side questions for a local AI chatbot, without rereading the whole conversation.**

subchat is a terminal chatbot that runs entirely on your machine with open models. It has a main chat that remembers your conversation, and a **sub-chat** for quick side questions. Instead of sending the whole history to the model, a sub-chat finds the 3 most relevant past messages using local embeddings and sends only those. Fewer tokens, faster answers, and the main thread stays clean.

Built for the DEV Hacktoberfest 2026 challenge, "Slow and Steady" (`#devchallenge` `#hf26challenge`).

## Demo

<!-- Add a GIF or video link here -->
_Demo coming soon._

## Why it is "lazy" (on purpose)

- **You never scroll back.** Ask the sub-chat about something you said earlier and it finds it for you.
- **The model does less work.** A sub-chat sends 3 snippets, not the full history.
- **Side questions do not pollute the main chat.** Sub-chat questions and answers are not added to main history.

## How it works

```
main chat  ->  every message saved to main_memory.json
                      |
                      +-> embedded locally (all-MiniLM-L6-v2) into searchable memory

sub-chat   ->  your question is embedded
                      |
                      +-> top 3 similar past messages (questions are skipped)
                      +-> sent to the local LLM as background + your question
                      +-> reply shown, nothing saved to main history
```

- **Chat model:** Gemma 3 (4B) served locally by [Ollama](https://ollama.com)
- **Embeddings:** `all-MiniLM-L6-v2` via `sentence-transformers`
- **Persistence:** a local JSON file (`main_memory.json`)
- **Network calls:** only to `localhost` once the models are downloaded

## Why open models

- **Works offline.** After the one-time model downloads, no internet is needed.
- **Your data stays on your machine.** Chat history never leaves a local JSON file.
- **No API keys, no quotas, no cost.** No rate limits to hit mid-conversation.
- **Swappable.** Change the model with one environment variable.

## Quick start

Tested on Fedora Linux with an NVIDIA laptop GPU.

### 1. Install Ollama and pull the model

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma3:4b
```

Smaller GPU or CPU only? Try `gemma3:1b` and set `CHAT_MODEL=gemma3:1b`.

### 2. Set up Python

```bash
git clone https://github.com/YOUR_USERNAME/subchat.git
cd subchat
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The first run downloads the embedding model once, so you need internet for that step.

### 3. Run

```bash
cp .env.example .env    # optional, defaults work
python main.py
```

## Usage

| Input | What it does |
|-------|--------------|
| any message | Normal chat, saved to memory |
| `sub` | Enter sub-chat |
| `exit` (in sub-chat) | Return to main chat |
| `exit` (in main chat) | Quit |

Example:

```
You: my favorite language is Python and I use Fedora
Assistant: ...
You: sub
Sub-chat: what language do I like?
Sub-chat: You like Python.
```

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `LLM_URL` | `http://localhost:11434/v1/chat/completions` | Ollama's OpenAI-compatible endpoint |
| `CHAT_MODEL` | `gemma3:4b` | Any model you have pulled in Ollama |

## Results

<!-- Fill in after running the benchmark -->

| Approach | Tokens per sub-chat question | Latency |
|----------|-----------------------------|---------|
| Full history sent | _TBD_ | _TBD_ |
| Top-3 retrieval (subchat) | _TBD_ | _TBD_ |

## Known limitations

- A small embedding model finds topically related messages well, but can miss subtler intent such as specific verbs. A larger embedding model would improve this at the cost of speed.
- Small local chat models can drift or ignore context more than large hosted ones.
- Memory is rebuilt from `main_memory.json` at startup, which will get slower as history grows.
- Default context window in Ollama is 4096 tokens.

## Privacy note

`main_memory.json` contains your conversation history and is git-ignored. Do not commit it.

## License

[MIT](LICENSE). The models are not included in this repository and are used under their own licenses: Gemma under Google's Gemma terms, and all-MiniLM-L6-v2 under Apache 2.0. Check each model's page for current terms.