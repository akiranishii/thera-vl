/*
<ai_context>
Defines the database schema for meeting transcripts.
</ai_context>
*/

import { pgEnum, pgTable, text, timestamp, uuid, integer } from "drizzle-orm/pg-core"
import { meetingsTable } from "./meetings-schema"
import { agentsTable } from "./agents-schema"
import { relations } from "drizzle-orm"

export const messageRoleEnum = pgEnum("message_role", ["system", "user", "assistant"])

export const transcriptsTable = pgTable("transcripts", {
  id: uuid("id").defaultRandom().primaryKey(),
  meetingId: uuid("meeting_id")
    .references(() => meetingsTable.id, { onDelete: "cascade" })
    .notNull(),
  agentId: uuid("agent_id").references(() => agentsTable.id),
  agentName: text("agent_name"),
  role: messageRoleEnum("role").notNull(),
  content: text("content").notNull(),
  roundNumber: integer("round_number").default(0),
  sequenceNumber: integer("sequence_number").default(0),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at")
    .defaultNow()
    .notNull()
    .$onUpdate(() => new Date())
})

export const transcriptsRelations = relations(transcriptsTable, ({ one }) => ({
  meeting: one(meetingsTable, {
    fields: [transcriptsTable.meetingId],
    references: [meetingsTable.id]
  }),
  agent: one(agentsTable, {
    fields: [transcriptsTable.agentId],
    references: [agentsTable.id]
  })
}))

export type InsertTranscript = typeof transcriptsTable.$inferInsert
export type SelectTranscript = typeof transcriptsTable.$inferSelect 