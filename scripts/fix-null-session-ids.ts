import { db } from "@/db/db"
import { sessionsTable } from "@/db/schema"
import { eq } from "drizzle-orm"
import { sql } from "drizzle-orm/sql"

async function main() {
  console.log("Starting session ID fix script...")

  // First, check if the session_id column exists and add it if missing
  console.log("Checking if session_id column exists...")
  try {
    // Check for column existence
    const columnExists = await db.execute(
      sql`SELECT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'agents' AND column_name = 'session_id'
      ) as exists`
    )
    
    // Extract the result using the specific type of the returned data
    // The exact structure depends on the database driver and Drizzle version
    const result = columnExists as unknown as { rows: Array<{ exists: boolean }> }
    const columnExistsValue = result.rows?.[0]?.exists === true
    
    if (!columnExistsValue) {
      console.log("session_id column does not exist. Adding it now...")
      await db.execute(
        sql`ALTER TABLE "agents" ADD COLUMN "session_id" UUID`
      )
      console.log("session_id column added successfully.")
    } else {
      console.log("session_id column already exists.")
    }
  } catch (error) {
    console.error("Error checking/adding session_id column:", error)
    throw error
  }

  // Create a default session if none exists with this ID
  const defaultSessionId = "00000000-0000-0000-0000-000000000000"
  
  // Check if the default session exists
  const existingSession = await db.query.sessions.findFirst({
    where: eq(sessionsTable.id, defaultSessionId)
  })
  
  // If the default session doesn't exist, create it
  if (!existingSession) {
    console.log("Creating default session...")
    await db.insert(sessionsTable).values({
      id: defaultSessionId,
      title: "Default Migration Session",
      description: "Session created for agents with missing session IDs",
      isPublic: false,
      userId: "system",
      createdAt: new Date(),
      updatedAt: new Date()
    })
    console.log("Default session created.")
  } else {
    console.log("Default session already exists.")
  }
  
  // Use direct SQL to update agents with null session ID
  console.log("Updating agents with null session_id...")
  try {
    // Using the raw SQL query allows us to bypass type checking issues
    // since the schema might not match the actual database structure yet
    const result = await db.execute(
      sql`UPDATE agents SET session_id = ${defaultSessionId} WHERE session_id IS NULL`
    )
    console.log("Successfully updated agents with default session ID.")
    
    // Now add NOT NULL constraint
    console.log("Adding NOT NULL constraint to session_id...")
    await db.execute(
      sql`ALTER TABLE "agents" ALTER COLUMN "session_id" SET NOT NULL`
    )
    console.log("NOT NULL constraint added successfully.")
  } catch (error) {
    console.error("Error updating agents:", error)
    throw error
  }
  
  console.log("Session ID fix script completed.")
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Error running session ID fix script:", error)
    process.exit(1)
  }) 