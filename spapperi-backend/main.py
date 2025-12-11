from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from uuid import uuid4

app = FastAPI(title="Spapperi Backend (Reset)")

# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

@app.get("/")
def root():
    return {"status": "Backend OK"}

@app.post("/api/chat")
def chat(request: ChatRequest):
    cid = request.conversation_id or str(uuid4())
    return {
        "response": "OK - Backend Reset Successful.",
        "conversation_id": cid
    }
