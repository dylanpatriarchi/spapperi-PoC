from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Spapperi RAG API",
    description="Secure Backend for Spapperi Configuration Agent",
    version="0.1.0"
)

# CORS Configuration (Restrict to frontend container in production)
origins = [
    "http://localhost:3000",
    "http://spapperi-frontend:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthCheck(BaseModel):
    status: str = "ok"

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint to verify backend status."""
    return HealthCheck(status="healthy")

@app.get("/")
async def root():
    return {"message": "Spapperi RAG Backend is running securely."}

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = None

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main Chat Endpoint.
    1. Loads state from Postgres (using conversation_id).
    2. Runs LangGraph.
    3. Saves new state.
    4. Returns AI response.
    """
    # Placeholder for graph invocation
    # In real impl: response = app.invoke(inputs, config=thread_config)
    
    return {
        "response": f"Echo: {request.message}. (Backend is reachable, logic WIP)",
        "conversation_id": request.conversation_id or "new-uuid"
    }
