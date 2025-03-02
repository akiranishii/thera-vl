/*
<ai_context>
Defines the database schema for meetings (parallel runs).
</ai_context>
*/

import { boolean, integer, pgEnum, pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core"
import { sessionsTable, SelectSession } from "./sessions-schema"
import { relations } from "drizzle-orm"

export const meetingStatusEnum = pgEnum("meeting_status", ["pending", "in_progress", "completed", "failed"])

export const meetingsTable = pgTable("meetings", {
  id: uuid("id").defaultRandom().primaryKey(),
  sessionId: uuid("session_id")
    .references(() => sessionsTable.id, { onDelete: "cascade" })
    .notNull(),
  title: text("title"),
  agenda: text("agenda"),
  taskDescription: text("task_description"),
  maxRounds: integer("max_rounds").default(3),
  currentRound: integer("current_round").default(0),
  status: meetingStatusEnum("status").default("pending").notNull(),
  isParallel: boolean("is_parallel").default(false).notNull(),
  parallelIndex: integer("parallel_index").default(0),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at")
    .defaultNow()
    .notNull()
    .$onUpdate(() => new Date()),
  completedAt: timestamp("completed_at")
})

export const meetingsRelations = relations(meetingsTable, ({ one }) => ({
  session: one(sessionsTable, {
    fields: [meetingsTable.sessionId],
    references: [sessionsTable.id]
  })
}))

export type InsertMeeting = typeof meetingsTable.$inferInsert
export type SelectMeeting = typeof meetingsTable.$inferSelect

// Type that includes the session relation
export interface MeetingWithSession extends SelectMeeting {
  session: SelectSession
} 