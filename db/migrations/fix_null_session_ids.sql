-- Create a default session if none exists
INSERT INTO sessions (id, title, description, is_public, user_id, created_at, updated_at) 
SELECT 
  '00000000-0000-0000-0000-000000000000', 
  'Default Migration Session', 
  'Session created for agents with missing session IDs', 
  false, 
  'system', 
  NOW(), 
  NOW()
WHERE NOT EXISTS (
  SELECT 1 FROM sessions WHERE id = '00000000-0000-0000-0000-000000000000'
);

-- Update all agents with null session_id to use the default session
UPDATE agents 
SET session_id = '00000000-0000-0000-0000-000000000000' 
WHERE session_id IS NULL; 