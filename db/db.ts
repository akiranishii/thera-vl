/*
<ai_context>
Initializes the database connection and schema for the app.
</ai_context>
*/

import { 
  agentsTable,
  meetingsTable, 
  profilesTable, 
  sessionsTable, 
  todosTable, 
  transcriptsTable, 
  votesTable 
} from "@/db/schema"
import { config } from "dotenv"
import { drizzle } from "drizzle-orm/postgres-js"
import postgres from "postgres"

config({ path: ".env.local" })

const schema = {
  profiles: profilesTable,
  todos: todosTable,
  sessions: sessionsTable,
  agents: agentsTable,
  meetings: meetingsTable,
  transcripts: transcriptsTable,
  votes: votesTable
}

const client = postgres(process.env.DATABASE_URL!)

export const db = drizzle(client, { schema })
