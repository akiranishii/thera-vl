# Project Name
Thera Virtual Lab (Public Sharing Edition)

## Project Description
A multi-agent AI collaboration system integrated with Discord. Users can create and manage AI "agents" via slash commands in Discord, run simultaneous (parallel) brainstorming sessions, and optionally share the session transcripts on a public website. The external site allows real-time or post-hoc viewing of transcripts, with an optional public gallery and a voting/leaderboard mechanism.

## Target Audience
- Teams or individuals who want to brainstorm or research collaboratively with multiple AI agents
- Public users who are curious about AI-generated multi-agent sessions and want to explore and vote on interesting transcripts

## Desired Features

### Discord Bot & Commands
- [ ] Single Discord bot handling slash commands:
  - [ ] `/startlab` to begin a new lab session
  - [ ] `/create_agent` to create or update an agent
  - [ ] `/brainstorm` to start multi-agent brainstorming with parameters (`agenda`, `rounds`, `parallel_meetings`, etc.)
  - [ ] `/individual_meeting` for single-agent sessions
  - [ ] `/view_transcript` to retrieve logs or link to external site
  - [ ] `/endlab` to close out a session, with option to make it public
  - [ ] `/help` for command info

### Multi-Agent Management
- [ ] Ability to manually create agents  
- [ ] If no agents exist, prompt user to auto-generate them  
- [ ] Support different role types (e.g., PI, Scientist, Critic)

### Parallel Meetings
- [ ] Run multiple parallel meeting “threads” under a single brainstorming session
- [ ] Each parallel run’s transcript is stored separately but linked by the same session ID
- [ ] Provide a user-driven or automated final summary after parallel runs complete

### Public/Private Sessions
- [ ] Mark sessions as `public` or `private`
- [ ] Public sessions appear in a “gallery” on the external site for everyone to see
- [ ] Private sessions remain accessible only to the owner (and authorized collaborators), ensuring no accidental leaks
- [ ] Encryption in transit/at rest to protect data, especially for private sessions

### External Website
- [ ] **Real-time streaming** of transcripts using WebSockets or Server-Sent Events (SSE)
- [ ] User accounts required for voting (Discord OAuth or separate login system to be decided)
- [ ] Public gallery listing for all public sessions
- [ ] Thumbs-up/down voting system (net score calculation)
- [ ] Leaderboard or sorting by net votes, recency, etc.
- [ ] Final transcript export (HTML/PDF)

### Voting & Moderation
- [ ] Store up/down votes as integers for a net score
- [ ] Implement moderation tools to remove or flag inappropriate content
- [ ] Authentication required before voting (to avoid spam and manage user-based voting limits)

### Data Model & Storage
- [ ] Database tables for:
  - [ ] Sessions (public/private flags, owner info, disclaimers for public data)
  - [ ] Agents (name, role, expertise, etc.)
  - [ ] Meetings (agenda, transcripts, round count, parallel runs)
  - [ ] Votes (session or meeting ID, user ID, vote value)
  - [ ] Users (for the website, if not using Discord OAuth)
- [ ] Store transcripts for parallel runs separately but linked by session ID
- [ ] Encryption in transit and optional encryption at rest
- [ ] Support data deletion or anonymization for compliance (e.g., GDPR-like requests)

### Scalability & Concurrency
- [ ] Plan for moderate concurrency at launch, with a roadmap to shard or scale horizontally if usage grows significantly
- [ ] Efficient text/log storage for potentially large transcripts
- [ ] Consider asynchronous or event-driven architecture to handle multiple live sessions

### User Interface
- [ ] Start with a **simple, clear** interface for the public gallery and private session view
- [ ] Real-time updating transcript view (possibly using a minimalistic design first)
- [ ] Possible future enhancements:
  - [ ] Advanced filtering or searching of transcripts
  - [ ] Tagging or categorizing sessions

## Design Requests
- [ ] Provide minimal text responses in Discord; direct users to external site for full logs
- [ ] Implement disclaimers for public sessions: a user must explicitly consent to making content public
- [ ] Ensure a responsive UI suitable for both desktop and mobile
- [ ] Possibly add an admin/moderator interface to review flagged transcripts or handle reported content

## Other Notes
- [ ] Automatic summary generation can be added as an advanced feature
- [ ] Ensure data compliance with disclaimers and user deletion requests
- [ ] Decide on authentication strategy: Discord OAuth vs. separate credentials
- [ ] Potential for paid tiers if usage grows (limiting parallel runs, advanced agent roles, etc.)
- [ ] Logging usage for analytics, performance monitoring, and capacity planning

Discord Slash Command Reference (Plain Text Version)

Below is the final list of slash commands for the TheraLab Virtual system, detailing their parameters, example usage, and behavior. These commands are designed to orchestrate multi-agent brainstorming sessions, manage agents, and integrate with an external website for transcripts and public sharing.

1. /startlab Description: Initializes or resets a new lab session in the backend. Parameters: (None) Example Usage: /startlab Behavior:
    
    1. Creates or resets a “Lab Session” record in the system.
    2. Wipes any existing conversation logs for the user’s current session (if desired).
    3. Replies with a confirmation message (e.g., “New lab session started! Use /brainstorm or /create_agent.”).
2. /create_agent Description: Manually defines or updates an AI agent’s metadata (PI, Critic, or Scientist). Parameters:
    
    1. agent_name (string, required) – Example: “Biologist”, “Principal Investigator”, “Scientific Critic”
    2. expertise (string, optional) – Short descriptor of the agent’s domain (e.g., “Structural biology”)
    3. goal (string, optional) – The agent’s overarching objective (e.g., “Propose novel protein scaffolds”)
    4. role (string, optional) – The agent’s functional role in the conversation (e.g., “Critique and spot errors”) Example Usage: /create_agent agent_name:"Biologist" expertise:"Structural biology" goal:"Propose novel protein scaffolds" role:"Provide domain insights" Behavior:
    5. model - can choose between openai, anthropic, and mistral models
    6. Creates or updates an agent record for the current lab session in the backend.
    7. Replies with “Agent [agent_name] created/updated.”
3. /brainstorm Description: Initiates a multi-agent brainstorming session, typically involving all defined agents (PI, Scientist(s), Critic). Parameters:
    
    1. agenda (string, required) – The main topic or question to discuss.
    2. rounds (int, default=3) – Number of “round-robin” passes in the conversation.
    3. parallel_meetings (int, default=1) – How many parallel runs to execute (for separate threads).
    4. agenda_questions (string, optional) – Additional bullet points or clarifications.
    5. rules (string, optional) – Extra constraints or instructions (e.g., “Keep answers concise.”) Example Usage: /brainstorm agenda:"Design novel protein scaffolds" rounds:3 parallel_meetings:2 agenda_questions:"Focus on binding site A" rules:"Keep responses concise" Behavior:
    6. Checks if any agents exist in the current session.
        - If none, bot asks: “No agents found. Auto-generate default roles from your agenda? (Yes/No)” If yes -> Creates 1 Principal Investigator, 1 Scientific Critic, and 3 Scientists based on agenda If no -> The user must manually do /create_agent
    7. Launches rounds of discussion among all agents.
    8. If parallel_meetings > 1, spawns multiple parallel runs, each with a separate transcript.
    9. Posts a short excerpt or final summary in Discord, plus a link to the external website for the transcript.
4. /individual_meeting Description: Conducts a one-on-one discussion with a specified agent, optionally including Critic feedback. Parameters:
    
    1. agent_name (string, required) – Which agent to meet with
    2. agenda (string, required) – The specific topic or question for that agent
    3. rounds (int, default=3)
    4. include_critic (bool, default=false) – Whether to include the Critic after each agent response
    5. agenda_questions (string, optional)
    6. rules (string, optional) Example Usage: /individual_meeting agent_name:"Biologist" agenda:"Propose 3 new ideas" rounds:2 include_critic:true Behavior:
    7. If agent_name does not exist, prompts user to create it first.
    8. Runs the specified rounds. If include_critic=true, the Critic agent responds right after each of the agent’s messages.
    9. Posts a final short summary or excerpt in Discord, linking to the external site for full logs.
5. /view_transcript Description: Retrieves the current session’s transcript or a specific meeting’s logs. Parameters:
    
    - meeting_id (string, optional) – If provided, fetch logs for a specific meeting Example Usage: /view_transcript Behavior:
    
    1. Bot checks the session or meeting logs, compiles a partial or summarized transcript.
    2. Posts either the summary in Discord or a short snippet with a link to the external site for the entire conversation.
6. /endlab Description: Ends the current lab session and optionally shares it publicly. Parameters:
    
    - public (bool, default=false) – If true, the session is marked as public in the database and will appear in the public gallery on the external site Example Usage: /endlab public:true Behavior:
    
    1. Closes or archives the session in the backend.
    2. If public=true, sets is_public to true, so the session is published to the gallery.
    3. Posts final link to the transcript or summary in Discord: “Session ended. See for final logs.”
7. /help Description: Displays a short overview of all the bot’s slash commands and usage tips. Parameters: (None) Example Usage: /help Behavior:
    
    1. Lists each command and a brief explanation.
    2. Provides an official doc link or instructions on how to use the main features (if any).

Additional Notes

- Auto-Generation Defaults: If the user chooses auto-generate when no agents exist, the system spawns 1 PI agent, 1 Critic agent, and 3 Scientist agents (titles/roles derived from the agenda).
- Parallel Meetings: For parallel_meetings > 1, the system keeps separate transcripts for each parallel run and may merge or summarize them at the end.
- Links to External Site: In all major commands that produce output, the final or partial transcripts are accessible via an external website for real-time or post-hoc viewing.
- Public Sessions: Only appear on the external site’s public gallery if marked public:true during /endlab.