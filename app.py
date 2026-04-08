"""FastAPI application for the AI agent chatbot."""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

load_dotenv()

from agent.agent import Agent  # noqa: E402 – must be after load_dotenv

app = FastAPI(title="AI Agent Chatbot")

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

_agent = Agent()


# ---------- Request / Response models ----------

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    reply: str
    messages: list[dict]


# ---------- Routes ----------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    if not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured.")

    messages = [m.model_dump() for m in body.messages]
    reply, new_messages = await _agent.chat(messages)
    return ChatResponse(reply=reply, messages=new_messages)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
