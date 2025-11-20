-- ============================================================================
-- Add preference_sessions table for CrewAI chat feature
-- ============================================================================
-- 
-- Instructions:
-- 1. Open Supabase Dashboard
-- 2. Go to SQL Editor → New Query
-- 3. Copy and paste this script
-- 4. Click "Run"
--
-- ============================================================================

-- Create preference_sessions table
CREATE TABLE IF NOT EXISTS preference_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Extracted preferences
    service_type VARCHAR(50),
    budget_min DECIMAL(10, 2),
    budget_max DECIMAL(10, 2),
    time_urgency VARCHAR(20),
    artisan_preference TEXT,
    special_notes TEXT,
    
    -- Conversation tracking
    conversation_history JSONB NOT NULL DEFAULT '[]'::jsonb,
    ready_to_match BOOLEAN DEFAULT false NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_preference_sessions_user_id ON preference_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_preference_sessions_session_id ON preference_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_preference_sessions_ready_to_match ON preference_sessions(ready_to_match);

-- Trigger for auto-updating updated_at
CREATE TRIGGER update_preference_sessions_updated_at 
    BEFORE UPDATE ON preference_sessions
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Verify
SELECT 'preference_sessions table created successfully!' as status;

-- Check table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'preference_sessions'
ORDER BY ordinal_position;

