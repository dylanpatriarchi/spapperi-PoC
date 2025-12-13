"""
Export utility for generating TXT reports from conversations.
"""
import os
from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime
from app.services.db import db


class ExportService:
    """Generate and save conversation reports"""
    
    EXPORT_DIR = "/app/exports"
    
    @classmethod
    def ensure_export_dir(cls):
        """Ensure export directory exists"""
        os.makedirs(cls.EXPORT_DIR, exist_ok=True)
    
    @classmethod
    async def generate_txt_report(cls, conversation_id: UUID) -> str:
        """
        Generate comprehensive TXT report for conversation.
        
        Returns:
            File path of generated report
        """
        cls.ensure_export_dir()
        
        # Fetch conversation data
        conversation = await db.get_conversation(conversation_id)
        messages = await db.get_conversation_messages(conversation_id)
        config = await db.get_configuration_data(conversation_id)
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Build report content
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("REPORT CONFIGURAZIONE TRAPIANTATRICE SPAPPERI")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Data generazione: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        lines.append(f"Conversation ID: {conversation_id}")
        lines.append(f"Status: {conversation.get('status', 'unknown')}")
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
        
        # Conversation History
        lines.append("STORICO CONVERSAZIONE")
        lines.append("-" * 80)
        lines.append("")
        
        for msg in messages:
            role = msg['role'].upper()
            timestamp = msg['created_at'].strftime('%H:%M:%S')
            content = msg['content']
            
            if role == "USER":
                lines.append(f"[{timestamp}] UTENTE:")
                lines.append(f"  {content}")
            elif role == "ASSISTANT":
                lines.append(f"[{timestamp}] ASSISTENTE:")
                lines.append(f"  {content}")
            
            # Add image indicator if present
            if msg.get('image_url'):
                lines.append(f"  [Immagine allegata: {msg['image_url']}]")
            
            lines.append("")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
        
        # Configuration Data
        lines.append("DATI CONFIGURAZIONE RACCOLTI")
        lines.append("-" * 80)
        lines.append("")
        
        if config:
            lines.extend(cls._format_configuration(config))
        else:
            lines.append("Nessun dato configurazione disponibile.")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
        
        # Contact Info (if provided)
        if config and config.get('contact_email'):
            lines.append("INFORMAZIONI DI CONTATTO")
            lines.append("-" * 80)
            lines.append("")
            lines.append(f"Email: {config.get('contact_email', 'N/A')}")
            lines.append(f"Partita IVA: {config.get('vat_number', 'N/A')}")
            lines.append("")
            lines.append("=" * 80)
            lines.append("")
        
        # Footer
        lines.append("Grazie per aver utilizzato il configuratore Spapperi.")
        lines.append("Sarai ricontattato al più presto dal nostro team commerciale.")
        lines.append("")
        
        # Write to file
        filename = f"{conversation_id}.txt"
        filepath = os.path.join(cls.EXPORT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return filepath
    
    @classmethod
    def _format_configuration(cls, config: Dict[str, Any]) -> List[str]:
        """Format configuration data into readable lines"""
        lines = []
        
        # Phase 1: Plant
        lines.append("FASE 1: Caratteristiche della Pianta")
        lines.append("")
        lines.append(f"  Coltura: {config.get('crop_type', 'N/A')}")
        lines.append(f"  Tipo radice: {config.get('root_type', 'N/A')}")
        
        root_dim = config.get('root_dimensions')
        if root_dim and isinstance(root_dim, dict):
            lines.append(f"  Dimensioni radice:")
            lines.append(f"    A = {root_dim.get('A', 'N/A')} cm")
            lines.append(f"    B = {root_dim.get('B', 'N/A')} cm")
            lines.append(f"    C = {root_dim.get('C', 'N/A')} cm")
            lines.append(f"    D = {root_dim.get('D', 'N/A')} cm")
        
        lines.append("")
        
        # Phase 2: Layout
        lines.append("FASE 2: Sesto di Impianto")
        lines.append("")
        lines.append(f"  Tipologia: {config.get('row_type', 'N/A')}")
        
        layout = config.get('layout_details')
        if layout and isinstance(layout, dict):
            lines.append(f"  Interfila (IF): {layout.get('IF', 'N/A')} cm")
            lines.append(f"  Interpianta (IP): {layout.get('IP', 'N/A')} cm")
            if layout.get('IB'):
                lines.append(f"  Interbina (IB): {layout.get('IB')} cm")
        
        lines.append("")
        
        # Phase 3: Environment
        lines.append("FASE 3: Trapianto e Terreno")
        lines.append("")
        lines.append(f"  Ambiente: {config.get('environment', 'N/A')}")
        lines.append(f"  Su baula: {'Sì' if config.get('is_raised_bed') else 'No'}")
        
        if config.get('is_raised_bed'):
            bed = config.get('raised_bed_details', {})
            if isinstance(bed, dict):
                lines.append(f"    Altezza (AT): {bed.get('AT', 'N/A')} cm")
                lines.append(f"    Larghezza (LT): {bed.get('LT', 'N/A')} cm")
                lines.append(f"    Inter baula (IT): {bed.get('IT', 'N/A')} cm")
                lines.append(f"    Spazio tra baule (ST): {bed.get('ST', 'N/A')} cm")
        
        lines.append(f"  Con pacciamatura: {'Sì' if config.get('is_mulch') else 'No'}")
        
        if config.get('is_mulch'):
            mulch = config.get('mulch_details', {})
            if isinstance(mulch, dict):
                lines.append(f"    Larghezza telo (LP): {mulch.get('LP', 'N/A')} cm")
        
        lines.append(f"  Tipo terreno: {config.get('soil_type', 'N/A')}")
        lines.append("")
        
        # Phase 4: Tractor
        lines.append("FASE 4: Macchinario (Trattore)")
        lines.append("")
        lines.append(f"  Ruote interne: {config.get('wheel_distance_internal', 'N/A')} cm")
        lines.append(f"  Potenza: {config.get('tractor_hp', 'N/A')} HP")
        lines.append("")
        
        # Phase 5: Accessories
        lines.append("FASE 5: Accessori")
        lines.append("")
        
        acc_primary = config.get('accessories_primary', [])
        lines.append(f"  Accessori primari telaio: {', '.join(acc_primary) if acc_primary else 'Nessuno'}")
        
        acc_secondary = config.get('accessories_secondary', [])
        lines.append(f"  Accessori secondari:       {', '.join(acc_secondary) if acc_secondary else 'Nessuno'}")
        
        acc_element = config.get('accessories_element', [])
        lines.append(f"  Accessori di elemento:     {', '.join(acc_element) if acc_element else 'Nessuno'}")
        lines.append("")
        
        # Phase 6: Notes
        if config.get('user_notes'):
            lines.append("FASE 6: Note Aggiuntive")
            lines.append("")
            lines.append(f"  {config.get('user_notes')}")
            lines.append("")
        
        return lines


# Global instance
export_service = ExportService
