import { NextResponse } from "next/server"

export async function GET() {
  return NextResponse.json({
    isSuccess: true,
    message: "API is healthy",
    data: {
      timestamp: new Date().toISOString(),
      status: "online"
    }
  })
} 