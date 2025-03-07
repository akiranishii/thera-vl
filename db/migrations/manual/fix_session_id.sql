-- Fix missing session_id column and null values in agents table
-- First, check if the column exists
DO $$
BEGIN
    -- Check if the session_id column exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'agents' AND column_name = 'session_id'
    ) THEN
        -- Column doesn't exist, add it
        EXECUTE 'ALTER TABLE "agents" ADD COLUMN "session_id" UUID';
        RAISE NOTICE 'Added session_id column to agents table';
    ELSE
        RAISE NOTICE 'session_id column already exists';
    END IF;
END
$$;

-- Ensure the default session exists
INSERT INTO "sessions" ("id", "title", "description", "is_public", "user_id", "created_at", "updated_at")
SELECT 
  '00000000-0000-0000-0000-000000000000', 
  'Default Migration Session', 
  'Session created for agents with missing session IDs', 
  FALSE, 
  'system', 
  NOW(), 
  NOW()
WHERE NOT EXISTS (
  SELECT 1 FROM "sessions" WHERE "id" = '00000000-0000-0000-0000-000000000000'
);

-- Update all agents with null session_id to use default session
UPDATE "agents" 
SET "session_id" = '00000000-0000-0000-0000-000000000000' 
WHERE "session_id" IS NULL;

-- Add NOT NULL constraint (only do this after fixing the null values)
ALTER TABLE "agents" ALTER COLUMN "session_id" SET NOT NULL; 