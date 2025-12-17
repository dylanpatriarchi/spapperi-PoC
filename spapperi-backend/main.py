from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from uuid import UUID

from app.models.conversation import ChatRequest, ChatResponse
from app.services.db import db
from app.services.phase_manager import phase_manager
from app.services.db import db
from app.services.rag_service import rag_service
from app.services.pdf_service import generate_report
from app.utils.export import export_service
from app.services.openai_validator import ai_validator
from app.services.pdf_service import generate_report


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown"""
    # Startup
    await db.initialize()
    ai_validator.initialize()
    export_service.ensure_export_dir()
    print("✓ Database connection pool initialized")
    print("✓ OpenAI client initialized")
    print("✓ Export directory ready")
    
    yield
    
    # Shutdown
    await db.close()
    print("✓ Database connection pool closed")


app = FastAPI(
    title="Spapperi AI Configurator Backend",
    description="Conversational AI system for configuring planting machines",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "Backend OK", "version": "2.0.0"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main conversational endpoint.
    Handles user messages, validates responses, updates conversation state.
    """
    try:
        # Get or create conversation
        if request.conversation_id:
            try:
                conv_id = UUID(request.conversation_id)
                conversation = await db.get_conversation(conv_id)
                if not conversation:
                    # Conversation doesn't exist - create new one instead of error
                    print(f"Conversation {conv_id} not found, creating new...")
                    conv_id = await db.create_conversation()
                    conversation = await db.get_conversation(conv_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid conversation_id format")
        else:
            # New conversation
            conv_id = await db.create_conversation()
            conversation = await db.get_conversation(conv_id)
        
        current_phase = conversation['current_phase']
        
        # Save user message
        await db.save_message(
            conversation_id=conv_id,
            role="user",
            content=request.message
        )
        
        # Special case: Initial greeting
        if current_phase == "phase_1_1" and len(await db.get_conversation_messages(conv_id)) == 1:
            # First message ever - send welcome + first question
            question, image_url, ui_type, options = await phase_manager.get_next_question(conv_id, current_phase)
            welcome = f"Ciao! Sono l'assistente Spapperi per configurare la tua trapiantatrice.\n\n{question}"
            
            await db.save_message(
                conversation_id=conv_id,
                role="assistant",
                content=welcome,
                image_url=image_url
            )
            
            return ChatResponse(
                response=welcome,
                conversation_id=str(conv_id),
                current_phase=current_phase,
                image_url=image_url,
                is_complete=False,
                export_file=None,
                ui_type=ui_type,
                options=options
            )
        
        # Process user response with AI validation
        result = await phase_manager.process_user_response(
            conversation_id=conv_id,
            current_phase=current_phase,
            user_message=request.message
        )
        
        is_valid = result["is_valid"]
        next_phase = result["next_phase"]
        clarification = result.get("clarification_needed")
        
        # Log validation result for debugging
        print(f"Validation result for phase {current_phase}: valid={is_valid}, clarification={clarification}")
        
        if not is_valid:
            # Invalid/incomplete response - ask for clarification
            response_text = clarification or "Mi dispiace, non ho capito bene. Puoi essere più specifico?"
            
            print(f"Requesting clarification: {response_text}")
            
            await db.save_message(
                conversation_id=conv_id,
                role="assistant",
                content=response_text
            )
            
            return ChatResponse(
                response=response_text,
                conversation_id=str(conv_id),
                current_phase=current_phase,  # Stay in same phase
                is_complete=False
            )
        
        # Valid response - move to next phase
        await db.update_conversation_phase(conv_id, next_phase)
        
        # Check if conversation is complete
        if next_phase == "complete":
            # Generate export file
            await db.mark_conversation_complete(conv_id)
            
            # Generate TXT report (legacy/backup)
            await export_service.generate_txt_report(conv_id)
            
            # Generate PDF report
            # Generate PDF report
            config_data = await db.get_configuration_data(conv_id)
            
            # Generate RAG recommendation
            print("Generating product recommendation...")
            try:
                recommendation = await rag_service.generate_recommendation(config_data)
                print("Recommendation generated successfully")
            except Exception as e:
                print(f"Error generating recommendation: {e}")
                recommendation = None
            
            pdf_path = generate_report(config_data, f"spapperi_config_{conv_id}", recommendation)
            
            response_text = "Grazie! I dati sono stati registrati. Puoi scaricare il riepilogo in PDF qui sotto. 📄\n\nTi è stato inviato anche via mail. A presto! 🎉"
            
            await db.save_message(
                conversation_id=conv_id,
                role="assistant",
                content=response_text
            )
            
            return ChatResponse(
                response=response_text,
                conversation_id=str(conv_id),
                current_phase=next_phase,
                is_complete=True,
                export_file=f"/api/export/{conv_id}/pdf"
            )
        
        # Small delay to ensure DB writes complete before fetching for conditional logic
        import asyncio
        await asyncio.sleep(0.1)
        
        # Get next question (will fetch fresh data from DB for conditional logic)
        next_question, image_url, ui_type, options = await phase_manager.get_next_question(conv_id, next_phase)
        
        await db.save_message(
            conversation_id=conv_id,
            role="assistant",
            content=next_question,
            image_url=image_url
        )
        
        return ChatResponse(
            response=next_question,
            conversation_id=str(conv_id),
            current_phase=next_phase,
            image_url=image_url,
            is_complete=False,
            ui_type=ui_type,
            options=options
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/images/{path:path}")
async def serve_image(path: str):
    """
    Serve images from /app/source/images/ directory.
    Example: /api/images/configurator/size.png
    """
    image_path = f"/app/source/images/{path}"
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path)


@app.get("/api/export/{conversation_id}")
async def export_report(conversation_id: str):
    """
    Generate and download TXT report for a conversation.
    """
    try:
        conv_id = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    # Check if conversation exists
    conversation = await db.get_conversation(conv_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Generate report
    try:
        file_path = await export_service.generate_txt_report(conv_id)
        
        return FileResponse(
            file_path,
            media_type="text/plain",
            filename=f"configurazione_spapperi_{conversation_id}.txt"
        )
    except Exception as e:
        print(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")


@app.get("/api/export/{conversation_id}/pdf")
async def export_pdf_report(conversation_id: str):
    """
    Download PDF report for a conversation.
    """
    try:
        conv_id = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    # PDF functionality relies on file existing in exports directory
    # It should have been generated at completion.
    # If not, we could regenerate it, but let's try to find it.
    
    # For simplicity, we regenerate it to ensure it exists
    config_data = await db.get_configuration_data(conv_id)
    if not config_data:
        raise HTTPException(status_code=404, detail="Configuration not found")

    # Re-generate to ensure latest data and file existence
    # Re-generate to ensure latest data and file existence
    
    # Try to regenerate recommendation too if possible, or just generate without it if it's too slow for a download link?
    # Ideally should persist recommendation in DB, but for now let's regenerate it on fly or just pass None if we want speed.
    # Given it's a "Download PDF" button, user expects it. The chat flow already generated it and saved to file system. 
    # But here we are re-generating. Let's regenerate recommendation to be consistent.
    try:
        recommendation = await rag_service.generate_recommendation(config_data)
    except Exception:
        recommendation = None

    pdf_path = generate_report(config_data, f"spapperi_config_{conv_id}", recommendation)
    
    if pdf_path and os.path.exists(pdf_path):
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"configurazione_spapperi_{conversation_id}.pdf"
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")


@app.get("/api/conversation/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """
    Get complete conversation history (for debugging/admin).
    """
    try:
        conv_id = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    messages = await db.get_conversation_messages(conv_id)
    conversation = await db.get_conversation(conv_id)
    config = await db.get_configuration_data(conv_id)
    
    return {
        "conversation": conversation,
        "messages": messages,
        "configuration": config
    }
