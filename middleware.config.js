// This file is used to configure the Clerk middleware

module.exports = {
  // Discord bot API routes that should bypass authentication
  publicRoutes: [
    "/api/sessions/active",
    "/api/sessions",
    "/api/sessions/:id/end",
    "/api/agents",
    "/api/sessions/:id/agents",
    "/api/meetings",
    "/api/meetings/:id/end",
    "/api/transcripts"
  ]
} 