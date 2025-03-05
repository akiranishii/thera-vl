import { NextRequest, NextResponse } from "next/server"
import { db } from "@/db/db"
import { agentsTable } from "@/db/schema"
import { eq } from "drizzle-orm"

/**
 * API route for getting a specific agent by ID
 * GET /api/discord/agents/[id]
 */
export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const agentId = params.id

    if (!agentId) {
      return NextResponse.json(
        { isSuccess: false, message: "Agent ID is required", data: null },
        { status: 400 }
      )
    }

    // Get the agent
    const agent = await db.query.agents.findFirst({
      where: eq(agentsTable.id, agentId),
    })

    if (!agent) {
      return NextResponse.json(
        { isSuccess: false, message: "Agent not found", data: null },
        { status: 404 }
      )
    }

    return NextResponse.json({
      isSuccess: true,
      message: "Agent retrieved successfully",
      data: agent
    })
  } catch (error) {
    console.error("Error getting agent:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to get agent", data: null },
      { status: 500 }
    )
  }
}

/**
 * API route for updating a specific agent by ID
 * PUT /api/discord/agents/[id]
 */
export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const agentId = params.id

    if (!agentId) {
      return NextResponse.json(
        { isSuccess: false, message: "Agent ID is required", data: null },
        { status: 400 }
      )
    }

    // Get the request body
    const body = await req.json()
    const { name, role, description, expertise, model } = body

    // Update data object with non-null values
    const updateData: any = {}
    if (name !== undefined) updateData.name = name
    if (role !== undefined) updateData.role = role
    if (description !== undefined) updateData.description = description
    if (expertise !== undefined) updateData.expertise = expertise
    if (model !== undefined) updateData.model = model

    // Set updatedAt
    updateData.updatedAt = new Date()

    // Check if the agent exists
    const existingAgent = await db.query.agents.findFirst({
      where: eq(agentsTable.id, agentId),
    })

    if (!existingAgent) {
      return NextResponse.json(
        { isSuccess: false, message: "Agent not found", data: null },
        { status: 404 }
      )
    }

    // Update the agent
    const [updatedAgent] = await db
      .update(agentsTable)
      .set(updateData)
      .where(eq(agentsTable.id, agentId))
      .returning()

    return NextResponse.json({
      isSuccess: true,
      message: "Agent updated successfully",
      data: updatedAgent
    })
  } catch (error) {
    console.error("Error updating agent:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to update agent", data: null },
      { status: 500 }
    )
  }
}

/**
 * API route for deleting a specific agent by ID
 * DELETE /api/discord/agents/[id]
 */
export async function DELETE(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const agentId = params.id

    if (!agentId) {
      return NextResponse.json(
        { isSuccess: false, message: "Agent ID is required", data: null },
        { status: 400 }
      )
    }

    // Check if the agent exists
    const existingAgent = await db.query.agents.findFirst({
      where: eq(agentsTable.id, agentId),
    })

    if (!existingAgent) {
      return NextResponse.json(
        { isSuccess: false, message: "Agent not found", data: null },
        { status: 404 }
      )
    }

    // Delete the agent
    await db
      .delete(agentsTable)
      .where(eq(agentsTable.id, agentId))

    return NextResponse.json({
      isSuccess: true,
      message: "Agent deleted successfully",
      data: null
    })
  } catch (error) {
    console.error("Error deleting agent:", error)
    return NextResponse.json(
      { isSuccess: false, message: "Failed to delete agent", data: null },
      { status: 500 }
    )
  }
} 