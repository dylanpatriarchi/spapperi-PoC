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
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Validate if user response is complete and extract data.
        
        Args:
            phase: Current conversation phase (e.g. "phase_1_1")
            user_message: User's input message
            expected_format: Description of expected format
            context: Additional context about the question
        
        Returns:
            {
                "is_complete": bool,
                "extracted_data": dict | None,
                "clarification_needed": str | None
            }
        """
        system_prompt = """Sei un assistente esperto nella configurazione di trapiantatrici agricole.
Il tuo compito è validare le risposte degli utenti durante un processo di configurazione guidato.

Per ogni risposta dell'utente, devi determinare:
1. Se la risposta è COMPLETA e VALIDA per la domanda posta
2. Estrarre i dati dalla risposta in formato strutturato
3. Se la risposta è incompleta/ambigua, indicare quale chiarimento serve

Rispondi SEMPRE in formato JSON con questa struttura:
{
    "is_complete": true/false,
    "extracted_data": {...} o null,
    "clarification_needed": "..." o null
}"""

        user_prompt = f"""**FASE**: {phase}
**DOMANDA**: {context}
**FORMATO ATTESO**: {expected_format}
**RISPOSTA UTENTE**: "{user_message}"

Valida se la risposta è completa ed estrai i dati."""

        try:
            response = await cls.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"OpenAI validation error: {e}")
            # Fallback: accept response as-is
            return {
                "is_complete": True,
                "extracted_data": {"raw": user_message},
                "clarification_needed": None
            }


# Global instance
ai_validator = OpenAIValidator
