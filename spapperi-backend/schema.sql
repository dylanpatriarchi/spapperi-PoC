-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table (for future Dashboard Auth)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations (The "Memory" of the Agent)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id), -- Optional for anonymous chat initially
    checkpoints JSONB, -- LangGraph Checkpoint Blob
    current_phase TEXT DEFAULT 'phase_1_1', -- Current conversation phase (FSM state)
    status TEXT DEFAULT 'active', -- active | completed | abandoned
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table for complete conversation history
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL, -- 'user' | 'assistant' | 'system'
    content TEXT NOT NULL,
    image_url TEXT, -- Optional: URL immagine allegata (es: size.png)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at);

-- Collected Configurations (Structured Data)
CREATE TABLE IF NOT EXISTS configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    
    -- PHASE 1: Plant
    crop_type TEXT,
    root_type TEXT,
    root_dimensions JSONB, -- {A, B, C, D}
    
    -- PHASE 2: Layout
    row_type TEXT, -- Single/Twin
    layout_details JSONB, -- {IF, IP, IB}
    
    -- PHASE 3: Environment
    environment TEXT, -- Open Field/Greenhouse
    is_raised_bed BOOLEAN,
    raised_bed_details JSONB,
    is_mulch BOOLEAN,
    mulch_details JSONB,
    soil_type TEXT,
    
    -- PHASE 4: Tractor
    wheel_distance_internal NUMERIC,
    wheel_distance_external NUMERIC,
    tractor_hp INTEGER,
    lift_category TEXT,
    has_auto_drive BOOLEAN,
    gps_model TEXT,
    
    -- PHASE 5: Accessories
    accessories_primary TEXT[],
    accessories_secondary TEXT[],
    accessories_element TEXT[],
    
    -- PHASE 6: Closing
    user_notes TEXT,
    is_interested BOOLEAN,
    contact_email TEXT,
    vat_number TEXT,
    
    is_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies (Security Layer)
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE configurations ENABLE ROW LEVEL SECURITY;

-- For now, allow all (will restrict once Auth is integrated)
-- For now, allow all (will restrict once Auth is integrated)
DROP POLICY IF EXISTS "Allow public access for POC" ON conversations;
CREATE POLICY "Allow public access for POC" ON conversations FOR ALL USING (true);

DROP POLICY IF EXISTS "Allow public access for POC" ON configurations;
CREATE POLICY "Allow public access for POC" ON configurations FOR ALL USING (true);
