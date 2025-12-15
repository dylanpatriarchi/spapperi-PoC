"""
Phase Manager: Finite State Machine for managing conversation flow.
Handles 6 main phases with 15+ sub-phases and conditional logic.
"""
from typing import Dict, Any, Optional, Tuple
from uuid import UUID
from app.services.openai_validator import ai_validator
from app.services.db import db


class PhaseManager:
    """
    Manages conversation phase transitions and question flow.
    """
    
    # Phase definitions with question templates and validation
    PHASES = {
        "phase_1_1": {
            "question": "Per iniziare, potresti indicarmi cosa devi trapiantare?",
            "expected_format": "Testo libero: nome della coltura (es: pomodori, insalata, fragole)",
            "field": "crop_type",
            "next_phase": "phase_1_2"
        },
        "phase_1_2": {
            "question": "Perfetto. Qual è la caratteristica della radice?",
            "expected_format": "Tipo di radice (es: Radice Nuda, Zolla Cubica, Zolla Conica, Zolla Piramidale)",
            "field": "root_type",
            "ui_type": "radio",
            "options": [
                "Radice Nuda",
                "Zolla Cubica",
                "Zolla Conica",
                "Zolla Piramidale"
            ],
            "next_phase": "phase_1_3"
        },
        "phase_1_3": {
            "question": "Ho bisogno delle dimensioni della zolla/radice (A, B, C, D). Elenca le misure per A, B, C e D in cm.",
            "expected_format": "4 valori numerici per A, B, C, D in centimetri",
            "field": "root_dimensions",
            "image": "/api/images/configurator/size.png",
            "next_phase": "phase_2_1"
        },
        "phase_2_1": {
            "question": "Passiamo al sesto di impianto. Si tratta di file singole o file binate?",
            "expected_format": "Scelta: Singole o Binate",
            "field": "row_type",
            "next_phase": "phase_2_2"
        },
        "phase_2_2": {
            "question": lambda data: (
                print(f"DEBUG phase_2_2: row_type = {data.get('row_type')}") or
                "Inserisci il numero di file, l'interfila (IF) in cm e l'interpianta (IP) in cm."
                if (data.get("row_type") or "").lower() in ["singole", "singolo", "single"]
                else "Inserisci il numero di bine, l'interfila (IF) in cm, l'interpianta (IP) in cm e l'interbina (IB) in cm."
            ),
            "expected_format": lambda data: (
                "3 valori: numero file, IF (cm), IP (cm)"
                if (data.get("row_type") or "").lower() in ["singole", "singolo", "single"]
                else "4 valori: numero bine, IF (cm), IP (cm), IB (cm)"
            ),
            "field": "layout_details",
            "next_phase": "phase_3_1"
        },
        "phase_3_1": {
            "question": "Il trapianto avverrà in campo aperto o sotto serra?",
            "expected_format": "Campo aperto o Serra",
            "field": "environment",
            "next_phase": "phase_3_2"
        },
        "phase_3_2": {
            "question": "Il trapianto viene effettuato su baula?",
            "expected_format": "Sì o No. Se Sì, specificare Altezza baula (AT), Larghezza (LT), Inter baula (IT) e Spazio tra baule (ST) in cm.",
            "field": "is_raised_bed",
            "next_phase": "phase_3_3"
        },
        "phase_3_3": {
            "question": "Il trapianto viene effettuato sopra pacciamatura?",
            "expected_format": "Sì o No. Se Sì, specificare Larghezza telo (LP) in cm.",
            "field": "is_mulch",
            "next_phase": "phase_3_4"
        },
        "phase_3_4": {
            "question": "Invece qual è la tipologia del terreno?",
            "expected_format": "Scelta tra Argilloso o Sabbioso",
            "field": "soil_type",
            "ui_type": "radio",
            "options": [
                "Argilloso / Tenace",
                "Sabbioso / Leggero"
            ],
            "next_phase": "phase_4_1"
        },
        "phase_4_1": {
            "question": "Dammi qualche info sul trattore. Qual è la misura interna delle ruote in cm?",
            "expected_format": "Valore numerico in centimetri",
            "field": "wheel_distance",
            "next_phase": "phase_4_2"
        },
        "phase_4_2": {
            "question": "Quanti cavalli (HP) ha il trattore?",
            "expected_format": "Valore numerico (HP)",
            "field": "tractor_hp",
            "next_phase": "phase_5_1"
        },
        "phase_5_1": {
            "question": "Seleziona gli accessori primari di telaio necessari:",
            "expected_format": "Lista di accessori scelti (anche vuota)",
            "field": "accessories_primary",
            "ui_type": "checkbox",
            "options": [
                "Nessuno",
                "Spandiconcime",
                "Innaffiamento localizzato",
                "Innaffiamento in continuo",
                "Stendi Manicrietta",
                "Ripiani Porta Alveoli",
                "Ripiani supplementari"
            ],
            "next_phase": "phase_5_2"
        },
        "phase_5_2": {
            "question": "Seleziona gli accessori secondari di telaio:",
            "expected_format": "Lista di accessori scelti (anche vuota)",
            "field": "accessories_secondary",
            "ui_type": "checkbox",
            "options": [
                "Nessuno",
                "Separatore di zolle",
                "Tracciatori fila manuali",
                "Tracciatori fila idraulici"
            ],
            "next_phase": "phase_5_3"
        },
        "phase_5_3": {
            "question": "Infine, seleziona gli accessori di elemento:",
            "expected_format": "Lista di accessori scelti (anche vuota)",
            "field": "accessories_element",
            "ui_type": "checkbox",
            "options": [
                "Nessuno",
                "Microgranulatore",
                "Posa/interra ala gocciolante",
                "Coltello appisolo",
                "Rullo in gomma"
            ],
            "next_phase": "phase_6_1"
        },
        "phase_6_1": {
            "question": "Hai delle note o richieste particolari da aggiungere?",
            "expected_format": "Testo libero (o 'No' se non ci sono note)",
            "field": "user_notes",
            "next_phase": "phase_6_2"
        },
        "phase_6_2": {
            "question": "Sulla base di questi dati, sei interessato a ricevere informazioni commerciali o un preventivo?",
            "expected_format": "Sì o No",
            "field": "is_interested",
            "ui_type": "radio",
            "options": ["Sì", "No"],
            "next_phase": "phase_6_3"
        },
        "phase_6_3": {
            "question": "Perfetto. Lasciami la tua Partita IVA e la tua Email per ricontattarti con il report pronto.",
            "expected_format": "Partita IVA ed Email",
            "field": "contact_info",
            "next_phase": "complete"
        }
    }
    
    @classmethod
    async def get_next_question(
        cls,
        conversation_id: UUID,
        current_phase: str
    ) -> Tuple[str, Optional[str], Optional[str], Optional[list]]:
        """
        Get the next question to ask based on current phase.
        
        Returns:
            (question_text, image_url, ui_type, options)
        """
        phase_data = cls.PHASES.get(current_phase)
        if not phase_data:
            return ("Errore: fase non riconosciuta", None, None, None)
        
        # Get configuration data for conditional questions
        config = await db.get_configuration_data(conversation_id)
        data = config or {}
        
        print(f"DEBUG get_next_question: phase={current_phase}, config data={data}")
        
        # Generate question (might be callable for conditional logic)
        question = phase_data["question"]
        if callable(question):
            question = question(data)
        
        # Get image URL if present
        image_url = phase_data.get("image")
        
        # Get UI metadata (for checkbox rendering)
        ui_type = phase_data.get("ui_type")
        options = phase_data.get("options")
        
        return (question, image_url, ui_type, options)
    
    @classmethod
    async def process_user_response(
        cls,
        conversation_id: UUID,
        current_phase: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Process user response: validate, extract data, determine next phase.
        
        Returns:
            {
                "is_valid": bool,
                "next_phase": str,
                "extracted_data": dict,
                "clarification_needed": str | None
            }
        """
        phase_data = cls.PHASES.get(current_phase)
        if not phase_data:
            return {
                "is_valid": False,
                "next_phase": current_phase,
                "extracted_data": {},
                "clarification_needed": "Fase non valida"
            }
        
        # Get configuration data for conditional validation
        config = await db.get_configuration_data(conversation_id)
        data = config or {}
        
        # Get expected format (might be callable)
        expected_format = phase_data["expected_format"]
        if callable(expected_format):
            expected_format = expected_format(data)
        
        # Get question for context
        question = phase_data["question"]
        if callable(question):
            question = question(data)
        
        # Get conversation history for this phase (for context-aware validation)
        all_messages = await db.get_conversation_messages(conversation_id)
        
        # Find when current phase started and get messages since then
        phase_messages = []
        phase_started = False
        for msg in all_messages:
            # Detect phase start (assistant asks the question for this phase)
            if msg['role'] == 'assistant' and not phase_started:
                # Check if this message contains the current phase question
                if question[:50] in msg['content']:  # Match first 50 chars
                    phase_started = True
            elif phase_started:
                phase_messages.append(msg)
        
        # Validate with OpenAI, including conversation history
        validation = await ai_validator.validate_response(
            phase=current_phase,
            user_message=user_message,
            expected_format=expected_format,
            context=question,
            conversation_history=phase_messages
        )
        
        is_complete = validation.get("is_complete", False)
        extracted = validation.get("extracted_data", {})
        clarification = validation.get("clarification_needed")
        
        if not is_complete:
            return {
                "is_valid": False,
                "next_phase": current_phase,  # Stay in same phase
                "extracted_data": {},
                "clarification_needed": clarification
            }
        
        # Save extracted data to configuration
        field = phase_data["field"]
        await cls._save_field_data(conversation_id, field, extracted, data)
        
        # Determine next phase with conditional logic
        next_phase = await cls._determine_next_phase(current_phase, extracted, data)
        
        return {
            "is_valid": True,
            "next_phase": next_phase,
            "extracted_data": extracted,
            "clarification_needed": None
        }
    
    @classmethod
    async def _save_field_data(
        cls,
        conversation_id: UUID,
        field: str,
        extracted_data: Dict[str, Any],
        existing_data: Dict[str, Any]
    ):
        """Save extracted field data to configuration"""
        save_data = {}
        
        # Map extracted data to database fields
        if field == "crop_type":
            save_data["crop_type"] = extracted_data.get("crop_type") or extracted_data.get("raw")
        
        elif field == "root_type":
            save_data["root_type"] = extracted_data.get("root_type") or extracted_data.get("raw")
        
        elif field == "root_dimensions":
            save_data["root_dimensions"] = {
                "A": extracted_data.get("A"),
                "B": extracted_data.get("B"),
                "C": extracted_data.get("C"),
                "D": extracted_data.get("D")
            }
        
        elif field == "row_type":
            print(f"DEBUG save row_type: extracted_data = {extracted_data}")
            # Try multiple keys as GPT-4o might use different names
            save_data["row_type"] = (
                extracted_data.get("row_type") or 
                extracted_data.get("sesto_impianto") or
                extracted_data.get("type") or
                extracted_data.get("raw")
            )
            print(f"DEBUG save row_type: saving value = {save_data['row_type']}")
        
        
        elif field == "layout_details":
            save_data["layout_details"] = {
                "number_of_rows": extracted_data.get("number_of_rows") or extracted_data.get("rows"),
                "IF": extracted_data.get("IF"),
                "IP": extracted_data.get("IP"),
                "IB": extracted_data.get("IB")  # None for single rows
            }
        
        elif field == "environment":
            save_data["environment"] = extracted_data.get("environment") or extracted_data.get("raw")
        
        elif field == "is_raised_bed":
            is_raised = extracted_data.get("is_raised_bed", False)
            save_data["is_raised_bed"] = is_raised
            if is_raised:
                save_data["raised_bed_details"] = {
                    "AT": extracted_data.get("AT"),
                    "LT": extracted_data.get("LT"),
                    "IT": extracted_data.get("IT"),
                    "ST": extracted_data.get("ST")
                }
        
        elif field == "is_mulch":
            is_mulch = extracted_data.get("is_mulch", False)
            save_data["is_mulch"] = is_mulch
            if is_mulch:
                save_data["mulch_details"] = {
                    "LP": extracted_data.get("LP")
                }
        
        elif field == "soil_type":
            save_data["soil_type"] = extracted_data.get("soil_type") or extracted_data.get("raw")
        
        elif field == "wheel_distance":
            save_data["wheel_distance_internal"] = extracted_data.get("wheel_distance") or extracted_data.get("raw")
        
        elif field == "tractor_hp":
            save_data["tractor_hp"] = extracted_data.get("tractor_hp") or extracted_data.get("raw")
        
        elif field == "accessories_primary":
            save_data["accessories_primary"] = extracted_data.get("accessories", [])
        
        elif field == "accessories_secondary":
            save_data["accessories_secondary"] = extracted_data.get("accessories", [])
        
        elif field == "accessories_element":
            save_data["accessories_element"] = extracted_data.get("accessories", [])
        
        elif field == "user_notes":
            save_data["user_notes"] = extracted_data.get("notes") or extracted_data.get("raw")
        
        elif field == "is_interested":
            # Handle checkbox response ["Sì"] or ["No"]
            print(f"DEBUG is_interested: extracted_data = {extracted_data}")
            # OpenAI extracts as 'interested_in_commercial_info_or_quote'
            value = extracted_data.get("interested_in_commercial_info_or_quote") or extracted_data.get("raw", "")
            is_yes = "sì" in str(value).lower() or "si" in str(value).lower() or "yes" in str(value).lower()
            print(f"DEBUG is_interested: value='{value}', is_yes={is_yes}")
            save_data["is_interested"] = is_yes
        
        elif field == "contact_info":
            save_data["contact_email"] = extracted_data.get("email")
            save_data["vat_number"] = extracted_data.get("vat_number")
        
        await db.save_configuration_data(conversation_id, save_data)
    
    @classmethod
    async def _determine_next_phase(
        cls,
        current_phase: str,
        extracted_data: Dict[str, Any],
        configuration_data: Dict[str, Any]
    ) -> str:
        """Determine next phase with conditional logic"""
        
        # Special case: Skip phase 6.3 if user is not interested
        if current_phase == "phase_6_2":
            # OpenAI extracts as 'interested_in_commercial_info_or_quote'
            value = extracted_data.get("interested_in_commercial_info_or_quote", "")
            is_interested = "sì" in str(value).lower() or "si" in str(value).lower() or "yes" in str(value).lower()
            print(f"DEBUG next_phase: value='{value}', is_interested={is_interested}")
            if not is_interested:
                return "complete"  # Skip contact info collection
        
        # Default: use next_phase from phase definition
        phase_data = cls.PHASES.get(current_phase, {})
        return phase_data.get("next_phase", "complete")


# Global instance
phase_manager = PhaseManager
