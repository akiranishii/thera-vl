<specification_planning>

1. **Core System Architecture and Key Workflows**
    
    - **Discord Bot Architecture**
        
        - A Python-based Discord bot connects to the Discord API and handles slash commands.
        - Each slash command triggers specific logic (e.g., `/startlab` creates a session, `/brainstorm` starts the multi-agent discussion).
        - The bot interacts with large language model APIs (OpenAI, Anthropic, Mistral, etc.) to generate agent responses.
        - The bot saves transcripts, session data, and agent metadata in Postgres (via Drizzle ORM / Supabase).
    - **External Website Architecture**
        
        - Next.js 13 app, with server actions, connected to the same Postgres DB (hosted via Supabase).
        - Provides real-time or on-demand transcript viewing and a public gallery.
        - If session is public, it appears in the gallery. If private, only authorized users can view.
        - Users can vote on sessions, see leaderboards, and optionally follow real-time updates using WebSockets or SSE.
    - **Key Workflows**
        
        1. User executes `/startlab` in Discord → new session record in DB.
        2. User optionally defines agents with `/create_agent`.
        3. User runs `/brainstorm` or `/individual_meeting` → triggers multi-agent (or single-agent) discussion.
        4. System logs transcripts to DB in real time.
        5. Optionally share public link → session is displayed in the gallery.
        6. Users can vote on the session → updates votes in DB.
2. **Project Structure and Organization**
    
    - **Existing Next.js App** for the external website (public gallery, transcripts).
    - **Actions**
        - `actions/db`: Drizzle-based DB actions (create, read, update, delete).
        - `actions`: For external integrations (e.g., Stripe, future expansions).
    - **Python Discord Bot**
        - A separate Python process using the Discord.py or nextcord library.
        - Connects to LLM APIs, handles slash commands, reads/writes to the same Postgres DB.
3. **Detailed Feature Specifications**
    
    - **Discord Bot & Commands**
        
        - Single bot with slash commands: `/startlab`, `/create_agent`, `/update_agent`, `/brainstorm`, `/individual_meeting`, `/view_transcript`, `/endlab`, `/help`.
        - Minimal text in Discord responses, linking to external site for full transcripts.
        - Must handle ephemeral vs. public messages carefully.
    - **Multi-Agent Management**
        
        - Agents have roles (PI, Scientist, Critic, etc.).
        - Agents stored in DB (`agentsTable`) linked to a session.
        - If no agents exist, auto-generate default set.
    - **Parallel Meetings**
        
        - Implement parallel runs under the same session ID.
        - Each run is stored separately in the `meetingsTable` and `transcriptsTable`.
    - **Public/Private Sessions**
        
        - Mark session as `public` or `private` in DB.
        - Public sessions visible in gallery.
        - Private sessions only visible to the session owner and authorized collaborators.
    - **External Website**
        
        - Real-time or on-demand transcript streaming.
        - Voting system with scoreboard.
        - Public gallery listing all public sessions.
        - Possibly add advanced search, filtering in the future.
    - **Voting & Moderation**
        
        - Thumbs-up/down → integer net score.
        - Logged-in users can vote once per session.
        - Moderator tools to flag or remove sessions.
    - **Data Model & Storage**
        
        - Tables: Sessions, Agents, Meetings, Transcripts, Votes, Users.
        - Encryption in transit (HTTPS) and optional encryption at rest.
        - Deletion or anonymization upon request.
    - **Scalability & Concurrency**
        
        - Next.js serverless approach with Postgres.
        - Python-based Discord bot scaled on separate worker if needed.
    - **User Interface**
        
        - Minimalistic design for transcripts, with real-time updates.
        - Responsive layout for desktop and mobile.
4. **Database Schema Design**
    
    - **New Tables**
        1. `sessionsTable` – Tracks session ID, user ID, public/private, createdAt, updatedAt.
        2. `agentsTable` – Tracks agent name, role, session ID, model, expertise, etc.
        3. `meetingsTable` – Stores parallel meeting references, agenda, session ID, rounds.
        4. `transcriptsTable` – Stores individual messages from agents, references `meetingId`.
        5. `votesTable` – Tracks user vote on a session or meeting, storing a +/- 1 value.
5. **Server Actions & Integrations**
    
    - **Database Actions**
        
        - `createSessionAction`, `getSessionAction`, `updateSessionAction`, `deleteSessionAction`.
        - `createAgentAction`, `getAgentsAction`, `updateAgentAction`, `deleteAgentAction`.
        - `createMeetingAction`, `listMeetingsAction`, `updateMeetingAction`.
        - `createTranscriptRecordAction`, `getTranscriptAction`.
        - `createVoteAction`, `updateVoteAction`, `getVoteAction`.
    - **Other Actions**
        
        - WebSocket or SSE integration for real-time transcript streaming.
        - LLM API calls for multi-agent generation (in Python Discord bot).
        - Additional moderation actions, if needed.
6. **Design System & Component Architecture**
    
    - **Design System**
        - Use Tailwind, Shadcn components.
        - Colors from existing variables (background, foreground, accent, etc.).
        - Typography: Inter font (as shown in the project).
    - **Components**
        - Reusable UI components: forms, buttons, toggles, modals.
        - Gallery Page, Transcript Page, Voting UI, Leaderboard.
        - Many are server components for direct data fetching or client components for interaction.
7. **Authentication & Authorization**
    
    - Clerk is used for user auth.
    - Protected routes in Next.js (e.g., certain pages require sign-in).
    - Discord-based flows do not rely on Clerk for slash command usage. Discord user identity is separate.
8. **Data Flow & State Management**
    
    - **Discord → Python**
        - Slash commands → Python code queries DB → calls LLM → logs transcripts.
    - **Next.js → DB**
        - Server components fetch from DB with Drizzle.
        - Users read transcripts or public gallery.
        - Voting triggers server actions that update `votesTable`.
9. **Payment Integration**
    
    - Stripe is already integrated for potential paid tiers (Pro membership).
    - The multi-agent brainstorming might have limits for free vs. pro.
10. **Analytics Implementation**
    

- PostHog with client & server usage tracking.
- Track page views, user identity, event triggers (like session creation).

1. **Testing Strategy**

- **Unit Tests (Jest)**
    
    - Test server actions for DB operations and edge cases (e.g., missing session ID).
- **Integration Tests**
    
    - With Playwright or Cypress. Test multi-step flows (start lab → create agent → run brainstorm → end lab).
- **Discord Bot Testing**
    
    - Use ephemeral test server, mock or stub LLM calls.
- **Edge Cases**
    
    - Missing parameters in slash commands.
    - Attempting to make a private session public without user confirmation.
    - Overlapping parallel sessions, large transcripts.

</specification_planning>

```markdown
# Thera Virtual Lab (Public Sharing Edition) Technical Specification

## 1. System Overview

Thera Virtual Lab (Public Sharing Edition) is a multi-agent AI collaboration system integrated with Discord. Users initiate AI brainstorming sessions (labs) using a Discord bot. The system logs multi-agent transcripts, which can optionally be shared publicly on an external Next.js website. The external site provides real-time or post-hoc viewing, a public gallery, and a voting mechanism for interesting transcripts.

**Core Purpose & Value Proposition**  
- Streamline multi-agent brainstorming within Discord.  
- Provide a public or private record of AI discussions.  
- Allow sharing sessions publicly for visibility, feedback, and community engagement.  

**Key Workflows**  
1. **Session Creation**: A user in Discord runs `/startlab` → new session record in Postgres.  
2. **Agent Setup**: The user defines or updates agents with `/create_agent`, storing them in the DB.  
3. **Brainstorm**: The user runs `/brainstorm` or `/individual_meeting` to commence a multi-agent or single-agent discussion. The system calls LLM APIs to generate messages.  
4. **Transcript Storage**: The system captures all messages in transcripts, stored in the DB.  
5. **Session End**: The user ends the session with `/endlab`, optionally marking it public.  
6. **External Site**: The Next.js site displays transcripts. If public, it appears in a shared gallery and can be voted upon.  

**System Architecture**  
- **Discord Bot (Python)**  
  - Manages slash commands, orchestrates AI calls, stores data in Postgres via Drizzle.  
  - Real-time user interactions.  
- **Next.js 13 (Public Site)**  
  - Renders transcripts, public gallery, and voting.  
  - Reads/writes data from the same Postgres DB (hosted on Supabase).  
- **Database**  
  - Postgres with Drizzle ORM.  
  - Tables for sessions, agents, meetings, transcripts, votes, etc.  

## 2. Project Structure

Below is the proposed extension of the existing Next.js + Drizzle app structure to accommodate Thera Virtual Lab:

```

├── actions │ ├── db │ │ ├── profiles-actions.ts │ │ ├── todos-actions.ts │ │ ├── sessions-actions.ts <-- New DB actions for sessions │ │ ├── agents-actions.ts <-- New DB actions for agents │ │ ├── meetings-actions.ts <-- New DB actions for parallel meetings │ │ ├── transcripts-actions.ts <-- New DB actions for transcripts │ │ └── votes-actions.ts <-- New DB actions for votes │ └── stripe-actions.ts ├── ... ├── db │ ├── schema │ │ ├── index.ts │ │ ├── profiles-schema.ts │ │ ├── todos-schema.ts │ │ ├── sessions-schema.ts <-- New │ │ ├── agents-schema.ts <-- New │ │ ├── meetings-schema.ts <-- New │ │ ├── transcripts-schema.ts <-- New │ │ └── votes-schema.ts <-- New │ └── db.ts ├── ... ├── python-discord-bot │ ├── main.py <-- Python code for Discord slash commands │ ├── requirements.txt │ └── ... └── ...

```

## 3. Feature Specification

### 3.1 Discord Bot & Commands

#### User Story and Requirements
- Discord users can initiate AI brainstorming sessions with slash commands.  
- Minimize text in Discord; direct to external site for details.  
- Sessions can be private or public.  

#### Detailed Implementation Steps
1. **/startlab**  
   - Creates new session in `sessionsTable`.  
   - Returns confirmation.  

2. **/create_agent**  
   - Creates or updates agent in `agentsTable`.  
   - If agent with given name exists (for current session), update it; otherwise create new.  

3. **/update_agent**  
   - Similar to `create_agent` but specifically enforces update for an existing agent.  

4. **/brainstorm**  
   - Checks if agents exist. If none, prompts user to auto-generate default agents.  
   - Initiates N rounds of conversation among all agents.  
   - If `parallel_meetings > 1`, spawns multiple parallel runs (each is a `meeting` record).  

5. **/individual_meeting**  
   - One-on-one session with a specified agent. Optionally includes Critic agent after each round.  

6. **/view_transcript**  
   - Fetches transcript from DB, returns short snippet, plus external link.  

7. **/endlab**  
   - Marks session ended. If `public=true`, sets session to public.  
   - Provides final link to transcript or summary.  

8. **/help**  
   - Displays usage instructions for these commands.  

#### Error Handling and Edge Cases
- Attempting to brainstorm without an active session → return error.  
- Attempting to create agent without active session → prompt to run /startlab.  
- If user tries to end or view transcript for a session that doesn’t exist, return error.  

### 3.2 Multi-Agent Management

#### User Story and Requirements
- Users define or auto-generate a set of AI agents.  
- Each agent has a name, role, and optional expertise.  

#### Detailed Implementation
1. `agentsTable` with columns: `id, sessionId, name, role, expertise, model`, etc.  
2. On `/brainstorm`, retrieve all agents linked to the session. If empty, prompt user for auto-generation.  

#### Edge Cases
- Duplicate agent names. Possibly handle by returning an error or suffixing the name.  
- Agents must belong to a valid session.  

### 3.3 Parallel Meetings

#### Requirements
- The user can specify multiple parallel runs under a single session.  
- Each run’s transcript is separate but linked by the same session ID.  

#### Implementation Steps
1. `/brainstorm parallel_meetings:n` → Create `n` records in `meetingsTable`.  
2. For each meeting, run the same conversation flow in parallel.  
3. After completion, optionally produce a merged or separate summary.  

#### Edge Cases
- Large `n` could cause concurrency issues. Possibly limit maximum.  

### 3.4 Public/Private Sessions

#### Requirements
- Sessions can be public or private.  
- Public sessions are shown in a gallery on the external site.  

#### Implementation Steps
1. The `sessionsTable` includes a `public` boolean.  
2. On `/endlab public:true`, set that flag.  
3. The external site queries all sessions with `public == true` for the gallery.  

#### Edge Cases
- Changing a session from public to private if it’s already listed. This would hide it from the gallery.  

### 3.5 External Website

#### Requirements
- Real-time transcript updates (via SSE/WebSockets).  
- Public gallery listing all public sessions.  
- Voting system with scoreboard.  

#### Implementation Steps
1. **Gallery Page**: Server component fetching all sessions with `public=true`.  
2. **Transcript Page**: Server component fetching transcripts, possibly updated live.  
3. **WebSockets**: Python bot → a server push mechanism that broadcasts new messages. Or SSE from Next.js.  

#### Edge Cases
- If user attempts to view a private session, check ownership or collaboration permission.  

### 3.6 Voting & Moderation

#### Requirements
- Up/down vote on session. Net score stored in `votesTable`.  
- Must be logged in via Clerk to vote.  

#### Implementation Steps
1. **Vote**: A user calls `createVoteAction(sessionId, userId, +1 or -1)`.  
2. **Update Vote**: If user changes vote, the action updates the existing record.  
3. **Moderation**: Admin can remove or hide sessions.  

#### Edge Cases
- A user changes their vote multiple times → always update the existing record.  
- Prevent multiple votes from the same user on the same session.  

## 4. Database Schema

### 4.1 Tables

Below are new tables to support Thera Virtual Lab. Adjust naming as desired; ensure each table has timestamps:

#### `sessionsTable`
| Column       | Type     | Constraints                     | Description                                    |
|--------------|---------|---------------------------------|------------------------------------------------|
| `id`         | uuid     | primaryKey().defaultRandom()    | Unique session ID                              |
| `userId`     | text     | notNull()                       | Owner’s user ID                                |
| `isPublic`   | boolean  | default(false).notNull()        | True if session is public                     |
| `createdAt`  | timestamp| defaultNow().notNull()          | Creation time                                  |
| `updatedAt`  | timestamp| defaultNow().notNull().$onUpdate(...) | Last update time                     |

#### `agentsTable`
| Column       | Type    | Constraints                          | Description                                      |
|--------------|---------|--------------------------------------|--------------------------------------------------|
| `id`         | uuid    | primaryKey().defaultRandom()         | Unique agent ID                                  |
| `sessionId`  | uuid    | references(sessionsTable.id, cascade)| Link to session                                  |
| `name`       | text    | notNull()                            | Agent name                                       |
| `role`       | text    | notNull()                            | E.g., “PI”, “Scientist”, “Critic”                |
| `expertise`  | text    |                                      | Domain expertise                                 |
| `model`      | text    | default("openai")                    | Chosen LLM model (e.g., “anthropic”)             |
| `createdAt`  | timestamp| defaultNow().notNull()              | Creation time                                    |
| `updatedAt`  | timestamp| defaultNow().notNull().$onUpdate(...)| Last update time                                 |

#### `meetingsTable`
| Column       | Type    | Constraints                               | Description                    |
|--------------|---------|-------------------------------------------|--------------------------------|
| `id`         | uuid    | primaryKey().defaultRandom()              | Unique meeting ID              |
| `sessionId`  | uuid    | references(sessionsTable.id, cascade)     | Link to parent session         |
| `agenda`     | text    | notNull()                                 | Meeting agenda                 |
| `rounds`     | int     | default(3).notNull()                      | Number of discussion rounds    |
| `createdAt`  | timestamp| defaultNow().notNull()                   | Creation time                  |
| `updatedAt`  | timestamp| defaultNow().notNull().$onUpdate(...)    | Last update time               |

#### `transcriptsTable`
| Column       | Type    | Constraints                                    | Description                             |
|--------------|---------|------------------------------------------------|-----------------------------------------|
| `id`         | uuid    | primaryKey().defaultRandom()                   | Unique transcript ID                    |
| `meetingId`  | uuid    | references(meetingsTable.id, cascade).notNull()| Link to a specific meeting              |
| `agentName`  | text    |                                                | Which agent spoke (store name or ID)    |
| `content`    | text    | notNull()                                      | The message content                     |
| `timestamp`  | timestamp| defaultNow().notNull()                        | When the message was sent              |

#### `votesTable`
| Column       | Type    | Constraints                                        | Description                                       |
|--------------|---------|----------------------------------------------------|---------------------------------------------------|
| `id`         | uuid    | primaryKey().defaultRandom()                       | Unique ID for the vote                            |
| `userId`     | text    | notNull()                                          | Clerk user ID                                     |
| `sessionId`  | uuid    | references(sessionsTable.id, cascade).notNull()    | Which session is being voted on                   |
| `value`      | int     | notNull()                                          | +1 or -1                                          |
| `createdAt`  | timestamp| defaultNow().notNull()                            | Creation time                                     |
| `updatedAt`  | timestamp| defaultNow().notNull().$onUpdate(...)             | Last update time (if user changes vote)           |

## 5. Server Actions

### 5.1 Database Actions

Each file in `actions/db` should return a Promise of `ActionState<T>`:

- **`sessions-actions.ts`**  
  - `createSessionAction(userId: string): Promise<ActionState<SelectSession>>`  
  - `getSessionAction(sessionId: string): Promise<ActionState<SelectSession>>`  
  - `updateSessionAction(sessionId: string, data: Partial<InsertSession>): Promise<ActionState<SelectSession>>`  
  - `deleteSessionAction(sessionId: string): Promise<ActionState<void>>`  

- **`agents-actions.ts`**  
  - `createAgentAction(sessionId: string, agentData: InsertAgent): Promise<...>`  
  - `updateAgentAction(agentId: string, partialAgent: Partial<InsertAgent>): Promise<...>`  
  - `getAgentsAction(sessionId: string): Promise<...>`  
  - `deleteAgentAction(agentId: string): Promise<...>`  

- **`meetings-actions.ts`**  
  - `createMeetingAction(sessionId: string, agenda: string, rounds: number): Promise<...>`  
  - `getMeetingsAction(sessionId: string): Promise<...>`  

- **`transcripts-actions.ts`**  
  - `createTranscriptAction(meetingId: string, content: string, agentName: string): Promise<...>`  
  - `getTranscriptAction(meetingId: string): Promise<...>`  

- **`votes-actions.ts`**  
  - `createOrUpdateVoteAction(sessionId: string, userId: string, value: number): Promise<...>`  
  - `getVoteAction(sessionId: string, userId: string): Promise<...>`  
  - `getVoteCountAction(sessionId: string): Promise<...>`  

### 5.2 Other Actions

- **WebSocket or SSE** for Real-Time Transcript  
  - Possibly implemented in a Next.js API route (`app/api/subscribe/transcript`) or via a library (e.g., `socket.io`).  
  - The Python bot triggers updates whenever new transcript lines are saved.  

- **Python Discord Bot**  
  - The Discord bot code is separate but also uses the DB.  
  - On each slash command, call DB actions (through direct Postgres connection or an internal API endpoint).  

## 6. Design System

### 6.1 Visual Style

- **Color Palette**  
  - Inheriting from existing tailwind theme:
    - `--background`, `--foreground`, `--primary`, `--accent`, etc.  

- **Typography**  
  - Using Inter (already integrated).  
  - Font sizes: tailwind defaults.  

- **Component Styling Patterns**  
  - Using Shadcn UI components for alerts, buttons, dialogs, etc.  

- **Spacing & Layout**  
  - Standard Tailwind spacing.  
  - Consistent use of container widths.  

### 6.2 Core Components

- **Public Gallery**  
  - Grid or list of public sessions. Show title, user, net votes.  
- **Transcript View**  
  - Real-time or static transcript. Each message labeled with agent name.  
  - Minimal design: list of messages.  
- **Voting Buttons**  
  - Up/down icons from `lucide-react`.  
  - Net score displayed.  

## 7. Component Architecture

### 7.1 Server Components

- **Gallery Page**  
  - A server component that fetches all sessions with `isPublic=true`.  
  - Sort them by net votes or recency.  
- **Transcript Page**  
  - A server component that fetches transcripts for the given session/meeting.  
  - Could wrap in `<Suspense>` if we do partial loading.  

### 7.2 Client Components

- **Voting UI**  
  - A client component with an onClick that calls `createOrUpdateVoteAction`.  
  - Updates local state to reflect new vote.  
- **Real-Time Transcript**  
  - A client component that opens a WebSocket or SSE subscription.  
  - Renders new messages as they arrive.  

## 8. Authentication & Authorization

- **Clerk** manages user sign-in, sign-up.  
- The site blocks certain pages (like private sessions) if the user is not the session owner or an authorized collaborator.  
- Next.js middleware checks user sign-in status for protected routes.  

## 9. Data Flow

- **Discord → Python Bot**  
  - Slash commands → fetch or update DB records → generate AI responses → store transcripts.  
- **Next.js**  
  - Server actions or server components fetch data from DB.  
  - Client components handle UI events (votes, etc.) → call server actions.  

## 10. Stripe Integration

- Already partially integrated to differentiate free vs. pro membership.  
- Potential future: limit the number of parallel meetings for free users, or advanced features for pro.  
- Webhook in `app/api/stripe/webhooks/route.ts` handles subscription updates.  

## 11. PostHog Analytics

- **Analytics Strategy**  
  - Track page views, session creation, voting events.  
- **Implementation**  
  - PostHog client is initialized in the app.  
  - Use `posthog.capture()` calls on key events (like “brainstorm started”, “session made public”).  

## 12. Testing

- **Unit Tests with Jest**  
  - Each DB action tested with valid/invalid data.  
  - Example: `createSessionAction` with valid user ID → success; with missing user ID → error.  

- **e2e Tests with Playwright**  
  - Full flow: user logs in → starts a lab → creates agent → runs brainstorm → ends lab → checks site.  
  - Voting flow: user visits a public session page → upvotes → net score updates.  

- **Discord Bot Testing**  
  - Mock slash commands in a test Discord server.  
  - Validate transcripts stored properly, parallel runs function as expected.  

```