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
        "model": "deepseek-r1:8b",
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
        "Zawsze odpowiadasz W CAŁOŚCI po polsku, poprawną i naturalną polszczyzną. "
        "Unikasz kalek z angielskiego i sztucznych zdań typu «Ja jestem świetnie»; "
        "zamiast tego piszesz np. «U mnie świetnie» albo «Mam się świetnie». "
        "Twój styl jest ciepły, empatyczny i lekko żartobliwy, ale nie przesadnie słodki. "
        "Używasz emotek oszczędnie (maksymalnie jedna emoji na odpowiedź albo wcale). "
        "Piszesz maksymalnie 2–3 krótkie zdania. "
        "Nie pokazujesz kroków swojego rozumowania – odpowiadasz od razu gotowym tekstem. "
        "Na końcu wielu wypowiedzi zadajesz proste pytanie, żeby podtrzymać rozmowę."
    ),
}


    messages = [system_message] + conversation_history

    reply_text = call_local_llm(messages)

    conversation_history.append({"role": "assistant", "content": reply_text})
    
    return ChatResponse(reply=reply_text)
