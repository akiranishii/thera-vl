/*
<ai_context>
Defines the database schema for AI agents.
</ai_context>
*/

import { pgEnum, pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core"

export const agentStatusEnum = pgEnum("agent_status", ["active", "inactive"])

export const agentsTable = pgTable("agents", {
  id: uuid("id").defaultRandom().primaryKey(),
  userId: text("user_id").notNull(),
  name: text("name").notNull(),
  description: text("description"),
  role: text("role").notNull(),
  expertise: text("expertise"),
  personality: text("personality"),
  status: agentStatusEnum("status").default("active").notNull(),
  prompt: text("prompt"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at")
    .defaultNow()
    .notNull()
    .$onUpdate(() => new Date())
})

export type InsertAgent = typeof agentsTable.$inferInsert
export type SelectAgent = typeof agentsTable.$inferSelect 