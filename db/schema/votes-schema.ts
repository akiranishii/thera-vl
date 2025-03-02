/*
<ai_context>
Defines the database schema for session votes.
</ai_context>
*/

import { integer, pgTable, text, timestamp, uuid, uniqueIndex } from "drizzle-orm/pg-core"
import { sessionsTable } from "./sessions-schema"
import { relations } from "drizzle-orm"

export const votesTable = pgTable("votes", {
  id: uuid("id").defaultRandom().primaryKey(),
  sessionId: uuid("session_id")
    .references(() => sessionsTable.id, { onDelete: "cascade" })
    .notNull(),
  userId: text("user_id").notNull(),
  value: integer("value").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at")
    .defaultNow()
    .notNull()
    .$onUpdate(() => new Date())
}, (table) => {
  return {
    userSessionIdx: uniqueIndex("votes_user_session_idx").on(table.userId, table.sessionId)
  }
})

export const votesRelations = relations(votesTable, ({ one }) => ({
  session: one(sessionsTable, {
    fields: [votesTable.sessionId],
    references: [sessionsTable.id]
  })
}))

export type InsertVote = typeof votesTable.$inferInsert
export type SelectVote = typeof votesTable.$inferSelect 