# AI Agent Chatbot

A conversational AI agent chatbot built with **FastAPI** and **OpenAI**, featuring a clean web UI and built-in tools.

## Features

- 💬 Multi-turn conversation with memory
- 🧮 **Calculator** – evaluate mathematical expressions
- 🕒 **Date & Time** – get the current UTC date/time
- 🔍 **Web Search** – pluggable search tool (demo stub included)
- 📐 **Unit Converter** – length, weight, and temperature conversions
- ⚡ Streaming-ready FastAPI backend
- 🎨 Responsive, accessible web UI

## Requirements

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/SunnyMok1999/AI_agent_chatbot.git
cd AI_agent_chatbot

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

## Running the Application

```bash
uvicorn app:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

## Project Structure

```
AI_agent_chatbot/
├── app.py              # FastAPI application entry point
├── agent/
│   ├── agent.py        # Agent loop (OpenAI + tool calls)
│   └── tools.py        # Tool implementations & OpenAI function definitions
├── templates/
│   └── index.html      # Web UI template
├── static/
│   ├── css/style.css   # Stylesheet
│   └── js/chat.js      # Frontend JavaScript
├── requirements.txt
└── .env.example
```

## Environment Variables

| Variable        | Description                          | Default        |
|-----------------|--------------------------------------|----------------|
| `OPENAI_API_KEY` | Your OpenAI API key (**required**)  | –              |
| `OPENAI_MODEL`  | OpenAI model to use                  | `gpt-4o-mini`  |

## Extending the Web Search Tool

The `search_web` function in `agent/tools.py` is a stub. To enable real web search, replace the function body with a call to a search API such as:

- [Brave Search API](https://brave.com/search/api/)
- [SerpAPI](https://serpapi.com/)
- [Bing Web Search API](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)

## License

MIT
