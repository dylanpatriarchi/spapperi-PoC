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

from langchain_core.messages import HumanMessage
from rag.graph import app as agent_app

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main Chat Endpoint.
    """
    # 1. Prepare Input
    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        # In a real app with checkpointer, "config" comes from DB. 
        # Here we need to pass it or rely on persistence.
        # For POC: We assume stateless or basic invocation.
    }

    # 2. Run Graph
    result = agent_app.invoke(initial_state)
    
    # 3. Extract Response
    bot_messages = result.get("messages", [])
    last_bot_msg = bot_messages[-1].content if bot_messages else "No response."
    
    # 4. Save Conversation ID (Mock)
    
    return {
        "response": last_bot_msg,
        "conversation_id": request.conversation_id or "new-uuid",
        "debug_state": result.get("config") # returning config for debugging
    }
