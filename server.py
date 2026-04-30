from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_brain import ask_ai

app = FastAPI()   # THIS MUST EXIST

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Atlas API running"}

@app.get("/chat")
def chat(msg: str):
    return {"reply": ask_ai(msg)}
