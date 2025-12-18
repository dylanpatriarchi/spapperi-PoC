
import os
import json
from uuid import UUID
from typing import Dict, Any, List, Optional
import asyncpg
from app.services.db import db
from openai import AsyncOpenAI

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RagService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.embedding_model = "text-embedding-3-small"

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for query text."""
        response = await client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return response.data[0].embedding

    async def search_similar_products(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search strictly for products using vector similarity."""
        embedding = await self.get_embedding(query)
        embedding_str = str(embedding)  # Format for pgvector input

        conn = await asyncpg.connect(self.db_url)
        try:
            # Using cosine distance (<=>) for similarity
            # Order by distance ASC (closest first)
            sql = """
                SELECT id, name, description, category, metadata, 
                       (embedding <=> $1) as distance
                FROM products
                ORDER BY distance ASC
                LIMIT $2
            """
            
            rows = await conn.fetch(sql, embedding_str, limit)
            
            results = []
            for row in rows:
                results.append({
                    "id": str(row["id"]),
                    "name": row["name"],
                    "description": row["description"],
                    "category": row["category"],
                    "distance": row["distance"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                })
            return results
        finally:
            await conn.close()

    async def generate_recommendation(self, config_data: Dict[str, Any]) -> str:
        """
        Generate a product recommendation based on full configuration.
        Returns a markdown string with the recommendation.
        """
        # 1. Construct a rich query from config
        query_parts = []
        if config_data.get("crop_type"):
            query_parts.append(f"Coltura: {config_data['crop_type']}")
        
        root_features = []
        if config_data.get("root_type"):
            root_features.append(config_data['root_type'])
        
        dims = config_data.get("root_dimensions", {})
        if any(dims.values()):
             dim_str = ", ".join([f"{k}:{v}" for k,v in dims.items() if v])
             root_features.append(f"Dimensioni: {dim_str}")
        
        if root_features:
            query_parts.append(f"Radice: {', '.join(root_features)}")

        layout = config_data.get("layout_details", {})
        if config_data.get("row_type"):
            query_parts.append(f"Sesto: {config_data['row_type']}")
        
        if config_data.get("is_raised_bed"):
             query_parts.append("Su baula")
        if config_data.get("is_mulch"):
             query_parts.append("Su pacciamatura")
        
        # Add accessories to query parts for context
        accessories = []
        if config_data.get("accessories_primary"):
             accessories.extend(config_data["accessories_primary"])
        if config_data.get("accessories_secondary"):
             accessories.extend(config_data["accessories_secondary"])
        if config_data.get("accessories_element"):
             accessories.extend(config_data["accessories_element"])
        
        if accessories:
            acc_str = ", ".join([a for a in accessories if a != "Nessuno"])
            if acc_str:
                query_parts.append(f"Accessori: {acc_str}")

        query_str = " ".join(query_parts)
        print(f"DEBUG RAG Query: {query_str}")

        # 2. Retrieve relevant context
        products = await self.search_similar_products(query_str, limit=3)
        
        if not products:
            return "Nessun prodotto specifico trovato nel catalogo per questa configurazione."

        # 3. Generate refined answer with GPT-4
        context_text = "\n\n".join([
            f"Prodotto: {p['name']}\nDescrizione: {p['description']}\nMetadata: {p['metadata']}"
            for p in products
        ])

        system_prompt = """
        Sei un esperto agronomo e tecnico commerciale Spapperi.
        Il tuo compito è generare una configurazione tecnica dettagliata per il modello TC12AM (o il modello più idoneo trovato).

        Nel report finale, scrivi una sezione intitolata "Consiglio dell'Esperto" seguendo QUESTA STRUTTURA:
        
        1. **Modello Identificato**: Conferma il modello (es. TC12AM) e spiega brevemente perché è adatto alla coltura/sesto indicati.
        2. **Configurazione Componenti**: ELENCA e SPIEGA i componenti/accessori selezionati dal cliente.
           - Per ogni accessorio (es. Spandiconcime, Microgranulatore, Ruote), spiega il suo ruolo tecnico nella configurazione specifica.
           - Esempio: "L'uso dello spandiconcime è essenziale per la coltura X su baula..."
        3. **Conclusione**: Un breve commento sulla qualità della configurazione.

        IMPORTANTE:
        - Non limitarti a elencare, SPIEGA IL PERCHÉ dei componenti in relazione al modello TC12AM.
        - Usa un tono professionale, "industrial" e tecnico.
        - Se mancano accessori critici, suggeriscili.
        """

        user_prompt = f"""
        DATI CONFIGURAZIONE CLIENTE:
        {query_str}

        TOKEN ACCESSORI SELEZIONATI:
        {acc_str if accessories else "Nessun accessorio selezionato"}

        PRODOTTI CATALOGO TROVATI:
        {context_text}

        Genera la descrizione tecnica della configurazione.
        """

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

rag_service = RagService()
