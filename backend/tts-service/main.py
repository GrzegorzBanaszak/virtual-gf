import os
import uuid
import pyttsx3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

app = FastAPI(title="Virtual GF - TTS Service")

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

class TtsRequest(BaseModel):
    text: str

class TtsResponse(BaseModel):
    file: str

engine = pyttsx3.init()
voices = engine.getProperty('voices')
polish_voice_id = None

for v in voices:
    # tu często będzie coś z 'PL' albo 'Polish' w nazwie, ale nie zawsze
    if "pl" in v.id.lower() or "polish" in v.name.lower():
        polish_voice_id = v.id
        break

if polish_voice_id:
    engine.setProperty('voice', polish_voice_id)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/tts", response_model=TtsResponse)
def tts(req: TtsRequest):
    """
    Przyjmuje tekst i generuje plik WAV z głosem.
    Zwraca nazwę pliku, który frontend potem może odtworzyć.
    """
    # unikalna nazwa pliku
    filename = f"{uuid.uuid4()}.wav"
    filepath = os.path.join(AUDIO_DIR, filename)

    # generowanie audio
    engine.save_to_file(req.text, filepath)
    engine.runAndWait()

    return TtsResponse(file=filename)

@app.get("/audio/{filename}")
def get_audio(filename: str):
    """
    Endpoint do pobrania pliku audio.
    """
    filepath = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(filepath):
        return {"error": "File not found"}
    return FileResponse(
        filepath,
        media_type="audio/wav",
        filename=filename
    )