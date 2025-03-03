/*
<ai_context>
Contains server actions related to agents in the DB.
</ai_context>
*/

"use server"

import { db } from "@/db/db"
import { InsertAgent, SelectAgent, agentsTable } from "@/db/schema/agents-schema"
import { ActionState } from "@/types"
import { auth } from "@clerk/nextjs/server"
import { and, eq } from "drizzle-orm"

export async function createAgentAction(
  agent: Omit<InsertAgent, "userId">
): Promise<ActionState<SelectAgent>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    const [newAgent] = await db
      .insert(agentsTable)
      .values({ ...agent, userId })
      .returning()

    return {
      isSuccess: true,
      message: "Agent created successfully",
      data: newAgent
    }
  } catch (error) {
    console.error("Error creating agent:", error)
    return { isSuccess: false, message: "Failed to create agent" }
  }
}

export async function getAgentsAction(): Promise<ActionState<SelectAgent[]>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    const agents = await db.query.agents.findMany({
      where: eq(agentsTable.userId, userId)
    })

    return {
      isSuccess: true,
      message: "Agents retrieved successfully",
      data: agents
    }
  } catch (error) {
    console.error("Error getting agents:", error)
    return { isSuccess: false, message: "Failed to get agents" }
  }
}

export async function getAgentAction(
  id: string
): Promise<ActionState<SelectAgent>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    const agent = await db.query.agents.findFirst({
      where: and(
        eq(agentsTable.id, id),
        eq(agentsTable.userId, userId)
      )
    })

    if (!agent) {
      return { isSuccess: false, message: "Agent not found" }
    }

    return {
      isSuccess: true,
      message: "Agent retrieved successfully",
      data: agent
    }
  } catch (error) {
    console.error("Error getting agent:", error)
    return { isSuccess: false, message: "Failed to get agent" }
  }
}

export async function updateAgentAction(
  id: string,
  data: Partial<InsertAgent>
): Promise<ActionState<SelectAgent>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Ensure the user owns the agent
    const agentToUpdate = await db.query.agents.findFirst({
      where: and(
        eq(agentsTable.id, id),
        eq(agentsTable.userId, userId)
      )
    })

    if (!agentToUpdate) {
      return { isSuccess: false, message: "Agent not found or unauthorized" }
    }

    const [updatedAgent] = await db
      .update(agentsTable)
      .set(data)
      .where(eq(agentsTable.id, id))
      .returning()

    return {
      isSuccess: true,
      message: "Agent updated successfully",
      data: updatedAgent
    }
  } catch (error) {
    console.error("Error updating agent:", error)
    return { isSuccess: false, message: "Failed to update agent" }
  }
}

export async function deleteAgentAction(
  id: string
): Promise<ActionState<void>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // Ensure the user owns the agent
    const agentToDelete = await db.query.agents.findFirst({
      where: and(
        eq(agentsTable.id, id),
        eq(agentsTable.userId, userId)
      )
    })

    if (!agentToDelete) {
      return { isSuccess: false, message: "Agent not found or unauthorized" }
    }

    await db.delete(agentsTable).where(eq(agentsTable.id, id))

    return {
      isSuccess: true,
      message: "Agent deleted successfully",
      data: undefined
    }
  } catch (error) {
    console.error("Error deleting agent:", error)
    return { isSuccess: false, message: "Failed to delete agent" }
  }
}

export async function getAgentsBySessionAction(
  sessionId: string
): Promise<ActionState<SelectAgent[]>> {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return { isSuccess: false, message: "Unauthorized" }
    }

    // For now, we'll just return all agents for the user
    // In a real implementation, you would filter by session ID if that relationship exists
    const agents = await db.query.agents.findMany({
      where: eq(agentsTable.userId, userId)
    })

    return {
      isSuccess: true,
      message: "Agents retrieved successfully",
      data: agents
    }
  } catch (error) {
    console.error("Error getting agents:", error)
    return { isSuccess: false, message: "Failed to get agents" }
  }
} 