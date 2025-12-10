from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
import json
from langchain_core.messages import HumanMessage
from rag.graph import app as agent_app

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

import psycopg2
from psycopg2.extras import RealDictCursor
import os

# DB Connection
def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def get_saved_config(conversation_id: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM configurations WHERE conversation_id = %s", (conversation_id,))
        row = cur.fetchone()
        if row:
            # Convert row to dict, filtering out None values if needed, 
            # but our state logic handles Nones.
            # We need to map DB columns to State keys if they differ.
            # luckily schema.sql columns match state.py keys mostly.
            return dict(row)
        return {}
    except Exception as e:
        print(f"DB Load Error: {e}")
        return {}
    finally:
        cur.close()
        conn.close()

def save_config(conversation_id: str, config: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Ensure conversation exists
        cur.execute("INSERT INTO conversations (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (conversation_id,))
        
        # Upsert Configuration
        # We constructed the columns dynamically or hardcoded map.
        # For POC, let's update specific fields that are present in config.
        # This is simple Upsert logic.
        
        # Filter config keys that match our schema
        valid_keys = [
            "crop_type", "root_type", "root_dimensions", "row_type", "layout_details",
            "environment", "is_raised_bed", "raised_bed_details", "is_mulch", "mulch_details",
            "soil_type", "wheel_distance_internal", "wheel_distance_external", "tractor_hp",
            "lift_category", "has_auto_drive", "gps_model", "accessories_primary",
            "accessories_secondary", "accessories_element", "user_notes", "contact_email", "vat_number"
        ]
        
        # Prepare columns and values
        filtered_config = {k: v for k, v in config.items() if k in valid_keys and v is not None}
        
        if not filtered_config:
            return

        columns = list(filtered_config.keys())
        values = list(filtered_config.values())
        
        # Dynamic SQL construction
        set_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns])
        col_names = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        
        query = f"""
            INSERT INTO configurations (conversation_id, {col_names})
            VALUES (%s, {placeholders})
            ON CONFLICT (conversation_id) 
            DO UPDATE SET {set_clause};
        """
        
        cur.execute(query, [conversation_id] + values)
        conn.commit()
    except Exception as e:
        print(f"DB Save Error: {e}")
    finally:
        cur.close()
        conn.close()

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main Chat Endpoint with Persistence.
    """
    conversation_id = request.conversation_id or str(uuid4())
    
    # 1. Load State
    saved_config = get_saved_config(conversation_id)
    print(f"--- Loaded Config for {conversation_id}: {saved_config} ---")
    
    # Determine the 'next_step' based on the LOADED config
    # We need to tell the Analyst what to look for.
    # Logic: If we have a stored config, we re-calculate what was the missing field
    # to know what the user is *answering* to right now.
    from rag.logic import get_next_missing_field
    expected_step = get_next_missing_field(saved_config)
    
    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "user_config": saved_config,
        "next_step": expected_step 
    }

    # 2. Run Graph
    result = agent_app.invoke(initial_state)
    
    # 3. Extract Response
    bot_messages = result.get("messages", [])
    last_bot_msg = bot_messages[-1].content if bot_messages else "No response."
    
    final_config = result.get("user_config", {})
    
    # 4. Save State
    save_config(conversation_id, final_config)
    
    return {
        "response": last_bot_msg,
        "conversation_id": conversation_id,
        "debug_state": final_config 
    }
