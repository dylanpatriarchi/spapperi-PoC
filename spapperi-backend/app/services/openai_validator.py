"""
OpenAI-based validation service for user responses.
Uses GPT-4 to validate if user input is complete/valid for current phase.
"""
import os
import json
from typing import Dict, Any, Optional
from openai import AsyncOpenAI


class OpenAIValidator:
    """Validates user responses using GPT-4"""
    
    client: Optional[AsyncOpenAI] = None
    
    @classmethod
    def initialize(cls):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        cls.client = AsyncOpenAI(api_key=api_key)
    
    @classmethod
    async def validate_response(
        cls,
        phase: str,
        user_message: str,
        expected_format: str,
        context: str = "",
        conversation_history: list = None
    ) -> Dict[str, Any]:
        """
        Validate if user response is complete and extract data.
        
        Args:
            phase: Current conversation phase (e.g. "phase_1_1")
            user_message: User's input message
            expected_format: Description of expected format
            context: Additional context about the question
            conversation_history: List of previous messages in current phase
        
        Returns:
            {
                "is_complete": bool,
                "extracted_data": dict | None,
                "clarification_needed": str | None
            }
        """
        system_prompt = """Sei un assistente esperto nella configurazione di trapiantatrici agricole.
Il tuo compito è validare RIGOROSAMENTE le risposte degli utenti durante un processo di configurazione guidato.

REGOLE DI VALIDAZIONE:
1. La risposta deve contenere TUTTE le informazioni richieste
2. I valori numerici devono essere plausibili per il contesto agricolo
3. Le scelte multiple devono corrispondere alle opzioni fornite
4. Se manca QUALSIASI informazione, segnala "is_complete": false

ESEMPI DI VALIDAZIONE:

Domanda: "Qual è la caratteristica della radice? Opzioni: 1. Radice Nuda 2. Zolla Cubica 3. Zolla Conica 4. Zolla Piramidale"
Risposta: "cubica" → ✅ is_complete: true, extracted_data: {"root_type": "Zolla Cubica"}
Risposta: "non lo so" → ❌ is_complete: false, clarification_needed: "Devi scegliere tra le 4 opzioni"

Domanda: "Dimensioni radice: A, B, C, D in cm"
Risposta: "A=3, B=3, C=4, D=5" → ✅ is_complete: true
Risposta: "A=3, B=3" → ❌ is_complete: false, clarification_needed: "Mancano i valori C e D"
Risposta: "circa 3 cm" → ❌ is_complete: false, clarification_needed: "Servono 4 valori distinti: A, B, C, D"

Domanda: "Numero bine, IF (cm), IP (cm), IB (cm)"
Risposta: "4 bine, IF 120, IP 30, IB 25" → ✅ is_complete: true
Risposta: "120 cm" → ❌ is_complete: false, clarification_needed: "Servono anche numero bine, IP e IB"

Rispondi SEMPRE in formato JSON:
{
    "is_complete": true/false,
    "extracted_data": {...} o null,
    "clarification_needed": "..." o null
}

IMPORTANTE: Se hai QUALSIASI dubbio sulla completezza, rispondi is_complete: false."""

        # Build conversation history context
        history_context = ""
        if conversation_history and len(conversation_history) > 0:
            history_context = "\n**MESSAGGI PRECEDENTI DELL'UTENTE IN QUESTA FASE**:\n"
            for i, msg in enumerate(conversation_history[-3:], 1):  # Last 3 messages
                if msg.get('role') == 'user':
                    history_context += f"{i}. \"{msg.get('content')}\"\n"
            history_context += "\nIMPORTANTE: Considera TUTTE le informazioni fornite nei messaggi precedenti. Se l'utente ha già dato alcuni valori, NON chiederli di nuovo.\n"

        user_prompt = f"""**FASE**: {phase}
**DOMANDA POSTA ALL'UTENTE**: 
{context}

**FORMATO RICHIESTO**: 
{expected_format}
{history_context}
**RISPOSTA CORRENTE DELL'UTENTE**: 
"{user_message}"

ANALIZZA con attenzione:
1. La risposta CORRENTE + i messaggi PRECEDENTI contengono TUTTE le informazioni?
2. I valori sono plausibili e sensati?
3. Se è una scelta multipla, corrisponde a un'opzione valida?

Valida RIGOROSAMENTE e restituisci JSON."""

        try:
            response = await cls.client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o which supports JSON mode
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0  # Zero temperature for consistent validation
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Additional validation: check if result has required fields
            if "is_complete" not in result:
                print(f"Warning: OpenAI response missing is_complete field: {result}")
                return {
                    "is_complete": False,
                    "extracted_data": None,
                    "clarification_needed": "Risposta non chiara. Puoi riformulare?"
                }
            
            return result
            
        except Exception as e:
            print(f"OpenAI validation error: {e}")
            # Fallback: reject response to be safe
            return {
                "is_complete": False,
                "extracted_data": None,
                "clarification_needed": "C'è stato un problema tecnico. Puoi ripetere la tua risposta?"
            }


# Global instance
ai_validator = OpenAIValidator
