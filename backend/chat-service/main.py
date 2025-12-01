from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import List, Dict

conversation_history: List[Dict] = []

app = FastAPI(title="Virtual GF - Chat Service")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def call_local_llm(messages: list[dict]) -> str:
    """
    Wywołanie lokalnego modelu przez API Ollama.
    """
    url = "http://localhost:11434/api/chat"

    payload = {
        "model": "llama3.1",
        "stream": False,
        "messages":messages
    }

    response = requests.post(url, json=payload)
    response.raise_for_status() 
    data = response.json()
    return data["message"]["content"]


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/hello")
def hello():
    return {"message": "Virtual GF chat service is running!"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):

    conversation_history.append({"role": "user", "content": req.message})

    system_message = {
        "role": "system",
        "content": (
            "Jesteś wirtualną dziewczyną (virtual girlfriend) o imieniu Lena. "
            "Odpowiadasz po polsku, w ciepły, wspierający, ale szczery sposób. "
            "Jesteś spokojna, empatyczna i trochę żartobliwa. "
            "Piszesz maksymalnie 3–4 krótkie zdania. "
            "Nie udzielasz porad medycznych ani finansowych – wtedy sugerujesz kontakt ze specjalistą. "
            "Nie używasz wulgaryzmów. Czasem zadajesz krótkie pytanie zwrotne, "
            "żeby podtrzymać rozmowę."
        ),
    }

    messages = [system_message] + conversation_history

    reply_text = call_local_llm(messages)

    conversation_history.append({"role": "assistant", "content": reply_text})
    
    return ChatResponse(reply=reply_text)
