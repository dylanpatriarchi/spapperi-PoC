"""
Database service with asyncpg connection pool and CRUD operations.
"""
import asyncpg
import os
import json
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class DatabaseService:
    """Singleton database service with connection pool"""
    
    pool: Optional[asyncpg.Pool] = None
    
    @classmethod
    async def initialize(cls):
        """Initialize connection pool"""
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        cls.pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        
        # Initialize Schema if needed
        await cls._init_schema()

    @classmethod
    async def _init_schema(cls):
        """Execute schema.sql to create tables if not exist"""
        schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "schema.sql")
        if not os.path.exists(schema_path):
             # Fallback for Docker path
             schema_path = "/app/schema.sql"
        
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema_sql = f.read()
                
            async with cls.pool.acquire() as conn:
                # Check if tables exist to avoid unnecessary work/errors
                # But IF NOT EXISTS in SQL handles it gracefully usually.
                # Let's just execute.
                try:
                    await conn.execute(schema_sql)
                    print("✓ Database schema initialized")
                except Exception as e:
                    print(f"Schema initialization warning: {e}")
        else:
            print(f"Warning: schema.sql not found at {schema_path}")
    
    @classmethod
    async def close(cls):
        """Close connection pool"""
        if cls.pool:
            await cls.pool.close()
    
    # === CONVERSATIONS ===
    
    @classmethod
    async def create_conversation(cls, user_id: Optional[UUID] = None) -> UUID:
        """Create new conversation and return its ID"""
        async with cls.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO conversations (user_id, current_phase, status)
                VALUES ($1, 'phase_1_1', 'active')
                RETURNING id
                """,
                user_id
            )
            return row['id']
    
    @classmethod
    async def get_conversation(cls, conversation_id: UUID) -> Optional[Dict[str, Any]]:
        """Get conversation by ID"""
        async with cls.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, user_id, current_phase, status, created_at, updated_at
                FROM conversations
                WHERE id = $1
                """,
                conversation_id
            )
            return dict(row) if row else None
    
    @classmethod
    async def update_conversation_phase(cls, conversation_id: UUID, phase: str):
        """Update current phase of conversation"""
        async with cls.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE conversations
                SET current_phase = $1, updated_at = NOW()
                WHERE id = $2
                """,
                phase,
                conversation_id
            )
    
    @classmethod
    async def mark_conversation_complete(cls, conversation_id: UUID):
        """Mark conversation as completed"""
        async with cls.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE conversations
                SET status = 'completed', updated_at = NOW()
                WHERE id = $1
                """,
                conversation_id
            )
    
    # === MESSAGES ===
    
    @classmethod
    async def save_message(
        cls,
        conversation_id: UUID,
        role: str,
        content: str,
        image_url: Optional[str] = None
    ) -> UUID:
        """Save message to database"""
        async with cls.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO messages (conversation_id, role, content, image_url)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                conversation_id,
                role,
                content,
                image_url
            )
            return row['id']
    
    @classmethod
    async def get_conversation_messages(
        cls,
        conversation_id: UUID,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all messages for a conversation"""
        async with cls.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, conversation_id, role, content, image_url, created_at
                FROM messages
                WHERE conversation_id = $1
                ORDER BY created_at ASC
                LIMIT $2
                """,
                conversation_id,
                limit
            )
            return [dict(row) for row in rows]
    
    # === CONFIGURATIONS ===
    
    @classmethod
    async def save_configuration_data(
        cls,
        conversation_id: UUID,
        data: Dict[str, Any]
    ):
        """Upsert configuration data"""
        async with cls.pool.acquire() as conn:
            # Check if exists
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM configurations WHERE conversation_id = $1)",
                conversation_id
            )
            
            if exists:
                # Build dynamic UPDATE based on provided fields
                set_clauses = []
                params = [conversation_id]
                param_idx = 2
                
                for key, value in data.items():
                    if key == 'conversation_id':
                        continue
                    set_clauses.append(f"{key} = ${param_idx}")
                    
                    # Handle JSONB fields
                    if isinstance(value, dict):
                        params.append(json.dumps(value))
                    elif isinstance(value, list):
                        params.append(value)
                    else:
                        params.append(value)
                    param_idx += 1
                
                if set_clauses:
                    query = f"""
                        UPDATE configurations
                        SET {', '.join(set_clauses)}
                        WHERE conversation_id = $1
                    """
                    await conn.execute(query, *params)
            else:
                # INSERT new record
                await conn.execute(
                    """
                    INSERT INTO configurations (conversation_id)
                    VALUES ($1)
                    """,
                    conversation_id
                )
                # Then update with data
                if data:
                    await cls.save_configuration_data(conversation_id, data)
    
    @classmethod
    async def get_configuration_data(
        cls,
        conversation_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get configuration data for conversation"""
        async with cls.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM configurations
                WHERE conversation_id = $1
                """,
                conversation_id
            )
            return dict(row) if row else None


# Global instance
db = DatabaseService
