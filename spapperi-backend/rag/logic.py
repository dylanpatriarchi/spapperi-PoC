from .state import ConfigurationState

def get_next_missing_field(config: ConfigurationState) -> str:
    """
    Scans the configuration state in order of the PDF flow 
    and returns the first missing field (None).
    """
    
    # PHASE 1: Plant
    if not config.get("crop_type"): return "crop_type"
    if not config.get("root_type"): return "root_type"
    if not config.get("root_dimensions"): return "root_dimensions"

    # PHASE 2: Layout
    if not config.get("row_type"): return "row_type"
    
    # Conditional Phase 2
    if config.get("row_type") == "File Singole":
        if not config.get("layout_details"): return "layout_details_single"
    elif config.get("row_type") == "File Binate":
        if not config.get("layout_details"): return "layout_details_twin"

    # PHASE 3: Environment
    if not config.get("environment"): return "environment"
    
    # Conditional Baula
    if config.get("is_raised_bed") is None: return "is_raised_bed"
    if config.get("is_raised_bed") is True and not config.get("raised_bed_details"): return "raised_bed_details"
    
    # Conditional Mulch
    if config.get("is_mulch") is None: return "is_mulch"
    if config.get("is_mulch") is True and not config.get("mulch_details"): return "mulch_details"
    
    if not config.get("soil_type"): return "soil_type"

    # PHASE 4: Tractor
    if not config.get("wheel_distance_internal"): return "wheel_distance_internal"
    # wheel_distance_external is optional, skip automatic check or ask "Do you want to specify?"
    # For now, let's assume we proceed after internal unless user specified both.
    
    if not config.get("tractor_hp"): return "tractor_hp"
    if not config.get("lift_category"): return "lift_category"
    
    if config.get("has_auto_drive") is None: return "has_auto_drive"
    if config.get("has_auto_drive") is True and not config.get("gps_model"): return "gps_model"

    # PHASE 5: Accessories
    # Arrays can be empty but we must have *asked* them. 
    # Validating this is trickier. We can use a special flag or check if it was processed.
    # For simplicity in this step-by-step function:
    if config.get("accessories_primary") is None: return "accessories_primary"
    if config.get("accessories_secondary") is None: return "accessories_secondary"
    if config.get("accessories_element") is None: return "accessories_element"

    # PHASE 6: Closing
    if config.get("user_notes") is None: return "user_notes" # Can be empty string
    if config.get("contact_email") is None: return "contact_email" # Or "declined"
    
    return "complete"

QUESTIONS = {
    "crop_type": "Per iniziare, potresti indicarmi la tipologia di coltura che devi trattare?",
    "root_type": "Perfetto. Qual è la caratteristica della radice? (Radice Nuda, Zolla Cubica, Conica o Piramidale?)",
    "root_dimensions": "Ho bisogno delle dimensioni della zolla/radice (A, B, C, D in cm).",
    "row_type": "Passiamo al sesto di impianto. Si tratta di file singole o file binate?",
    "layout_details_single": "Inserisci il numero di file, l'interfila (IF) in cm e l'interpianta (IP) in cm.",
    "layout_details_twin": "Inserisci il numero di bine, l'interfila (IF), l'interpianta (IP) e l'interbina (IB) in cm.",
    "environment": "Il trapianto avverrà in campo aperto o sotto serra?",
    "is_raised_bed": "Il trapianto viene effettuato su baula?",
    "raised_bed_details": "Specifica: Altezza baula (AT), Larghezza (LT), Inter baula (IT) e Spazio tra baule (ST) in cm.",
    "is_mulch": "Il trapianto viene effettuato sopra pacciamatura?",
    "mulch_details": "Specifica: Larghezza telo (LP), Larghezza fuori terra (LT), Inter telo (IT) e Spazio tra i teli (ST).",
    "soil_type": "Qual è la tipologia del terreno? (Argilloso/Tenace o Sabbioso/Leggero)",
    "wheel_distance_internal": "Passiamo al trattore. Qual è la misura interna della ruota in cm?",
    "tractor_hp": "Quanti cavalli (HP) ha il trattore e qual è la categoria del gancio?",
    "lift_category": "Categoria gancio (se non specificata prima)?",
    "has_auto_drive": "Il trattore è dotato di guida semi-automatica?",
    "gps_model": "Che marca e modello di GPS utilizza?",
    "accessories_primary": "Seleziona accessori primari di telaio (Spandiconcime, Innaffiamento, etc.) o scrivi 'nessuno'.",
    "accessories_secondary": "Seleziona accessori secondari di telaio (Separatore zolle, Tracciatori).",
    "accessories_element": "Seleziona accessori di elemento (Microgranulatore, Posa manichetta, etc.).",
    "user_notes": "Hai delle note o richieste particolari?",
    "contact_email": "Sei interessato a un preventivo? Se sì, lasciami la tua Email e P.IVA.",
}
