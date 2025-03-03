# Project Name
Thera Virtual Lab (Public Sharing Edition)

## Project Description
A multi-agent AI collaboration system integrated with Discord. Users can create and manage AI "agents" via slash commands in Discord, run simultaneous (parallel) brainstorming sessions, and optionally share the session transcripts on a public website. The external site allows real-time or post-hoc viewing of transcripts, with an optional public gallery and a voting/leaderboard mechanism.

## Target Audience
- Teams or individuals who want to brainstorm or research collaboratively with multiple AI agents
- Public users who are curious about AI-generated multi-agent sessions and want to explore and vote on interesting transcripts

## Desired Features

### Discord Bot & Commands (see end of document)

### Multi-Agent Management
- [ ] Ability to manually create agents  
- [ ] If no agents exist, prompt user to auto-generate them  
- [ ] Support different role types

### Parallel Meetings
- [ ] Run multiple parallel meeting “threads” under a single brainstorm session
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

# **Discord Slash Command Reference**

## **One-at-a-Time Sessions Overview**

- By default, you’ll have **only one active session** at a time.
- When you run `/lab start`, that new session becomes your single active “lab.”
- You can create agents, run team meetings, and review transcripts **within** that session.
- When you’re done, use `/lab end` to archive it.
- **Transcripts remain accessible** (via `/lab transcript view`) even after the session is ended.
- If you **do** want to “pick up where you left off” in an ended session, you can **reopen** the session (if you add a subcommand like `/lab reopen`), or


For simplicity, we’ll assume **no** concurrent sessions in this guide, so we don’t need a `/lab open session_id` or “switch” command. If you start a new session, the old one is either ended or overshadowed.

---

## **Top-Level Commands**

### 1. `/quickstart`

**Description**  
A single-step command for **new or casual** users to immediately create a lab session, spawn agents (Principal Investigator + multiple Scientists, optionally a Critic), and start a brainstorming session on the provided topic.

**Parameters**

- **topic** (string, required)  
    e.g., `"Gene therapy for rare diseases?"`
- **agent_count** (integer, optional, default=3)  
    Number of Scientist agents to create.
- **include_critic** (boolean, optional, default=true)  
    If `true`, also spawns a Critic agent.
- **public** (boolean, optional, default=false)  
    If `true`, creates a public session (`is_public=true`) in your external gallery.

**Example Usage**

```
/quickstart topic:"Optimizing CRISPR editing" agent_count:4 include_critic:false public:true
```

**Behavior**

1. **Creates** a new lab session (internally calls `/lab start`) using `title=topic` and `is_public=public`.
2. **Auto-generates**:
    - 1 Principal Investigator (PI).
    - `agent_count` Scientists.
    - An optional Critic if `include_critic=true`.
3. **Immediately starts** a multi-agent brainstorming meeting on `topic` (3 or so rounds by default).
4. **Replies** with a summary embed: “Quickstart completed! Created X agents and started a brainstorming session on [topic].”

---

### 2. `/lab`

**Description**  
Main **advanced** command group with multiple **subcommands** to fully control sessions, agents, data uploads, multi-agent meetings, transcripts, etc.

**Subcommands**:

| Subcommand           | Purpose                                         |
| -------------------- | ----------------------------------------------- |
| **start**            | Creates a new lab session                       |
| **end**              | Ends the current session                        |
| **list**             | Lists your sessions (active or recently ended)  |
| **agent create**     | Creates or updates an AI agent in the session   |
| **agent update**     | Updates an existing agent’s parameters          |
| **agent delete**     | Deletes an agent                                |
| **agent list**       | Lists all agents in the session                 |
| **team_meeting**     | Initiates a multi-agent discussion              |
| **end_team_meeting** | Ends an ongoing multi-agent meeting             |
| **transcript list**  | Lists available transcripts from prior meetings |
| **transcript view**  | Views a specific transcript by ID               |
| **reopen**           | Reopens a previously ended session              |

Below are each subcommand’s details.

---

#### 2A. `/lab start`

**Description**  
Creates a **new lab session** container for advanced workflows.

**Parameters**

- **title** (string, optional)  
    Defaults to something like `"Session #<UUID>"` if omitted.
- **is_public** (bool, optional, default=false)  
    Whether the session is publicly visible in your external gallery.
- **description** (string, optional)  
    Purpose or context for the session.

**Example Usage**

```
/lab start title:"Protein Modeling" is_public:false description:"Focus on novel folding approaches"
```

**Behavior**

1. Creates a new “Session” record in the backend with provided metadata.
2. This new session **becomes your active session** (superseding any prior session).
3. Bot replies: “Session started. ID = XYZ. Use `/lab agent create` to add agents or `/lab team_meeting` to begin a discussion.”
4. If a user tries `/lab start` while another session is active, prompt them to confirm or end the current session first.

---

#### 2B. `/lab end`

**Description**  
Ends or “archives” the current lab session so it’s no longer active.

**Parameters**

- **confirm** (boolean, optional, default=false)  
    When `true`, confirms you want to end the session.
- **public** (boolean, optional, default=false)  
    If `true`, marks the ended session as `is_public=true` (available in your gallery).

**Example Usage**

```
/lab end
```

or

```
/lab end confirm:true public:true
```

**Behavior**

1. Ends the active session in the backend.
2. If `public:true`, session is discoverable in the external gallery.
3. Bot posts a final embed or summary with a link to transcripts.
4. **One-at-a-time** note: Because you ended this session, the next time you run `/lab start`, that new session is your fresh “active” one.

---

#### 2C. `/lab list`

**Description**  
Lists active or recently ended sessions. With a one-at-a-time approach, typically only one session is active at a time.

**Parameters**

- _(Optional)_ filters like `limit`, `only_active`, etc.

**Example Usage**

```
/lab list
```

**Behavior**

1. Fetches relevant sessions for the user.
2. Displays each session’s ID, title, public status, etc.

---

#### 2D. `/lab agent create`

**Description**  
Creates a **new AI agent** in the _current_ lab session or updates one if `agent_name` already exists.

**Parameters**

1. **agent_name** (string, required)  
    E.g., `"Principal Investigator"`, `"Biologist"`, `"Critic"`.
2. **expertise** (string, optional)  
    Short descriptor (e.g., `"Structural biology"`).
3. **goal** (string, optional)  
    The agent’s main objective (e.g., `"Propose novel protein scaffolds"`).
4. **role** (string, optional)  
    Functional role (e.g., `"Provide domain insights"`).
5. **model** (string, optional)  
    Choose between supported LLM models (e.g., `"openai"`, `"anthropic"`, `"mistral"`).

**Example Usage**

```
/lab agent create agent_name:"Biologist" expertise:"Structural biology" goal:"Propose novel scaffolds" role:"Domain insights" model:"openai"
```

**Behavior**

1. Creates/updates the agent within the active session.
2. Bot replies: “Agent [agent_name] created/updated.”

---

#### 2E. `/lab agent update`

**Description**  
Updates parameters of an **existing agent** in the current session.

**Parameters**

- **agent_name** (string, required)  
    The agent to update.
- **expertise**, **goal**, **role**, **model** (optional)  
    Any fields that need updating.

**Example Usage**

```
/lab agent update agent_name:"Biologist" expertise:"Immunology" role:"Provide immunological insights"
```

**Behavior**

1. Locates the agent in the active session.
2. Updates the specified fields.
3. Bot replies: “Agent [agent_name] updated.”

---

#### 2F. `/lab agent delete`

**Description**  
Removes an AI agent from the current session.

**Parameters**

- **agent_name** (string, required)

**Example Usage**

```
/lab agent delete agent_name:"Biologist"
```

**Behavior**

1. Removes the agent record from the session.
2. Bot replies: “Agent [agent_name] deleted.”

---

#### 2G. `/lab agent list`

**Description**  
Lists **all agents** in the active session.

**Parameters**

- (Optional) filters, e.g. `role=Scientist`.

**Example Usage**

```
/lab agent list
```

**Behavior**

1. Retrieves and shows each agent’s name, role, expertise, etc.

---

#### 2H. `/lab team_meeting`

**Description**  
Starts a **multi-agent conversation** in the active session (brainstorm or discussion). Requires at least one PI agent in the session

**Parameters**

1. **agenda** (string, required)  
    The main topic or question.
2. **rounds** (int, optional, default=3)  
    Number of conversation rounds.
3. **parallel_meetings** (int, optional, default=1)  
    (Advanced) Number of parallel runs. Typically 1 for simplicity.
4. **agent_list** (string, optional)  
    Names/IDs of agents to include, comma-separated. If omitted, all session agents are used.
5. **auto_generate** (boolean, optional, default=false)  
    If true, automatically creates PI, critic, and 3 Scientist agents based on the `agenda`.
    **Optional Parameters (Only Used When `auto_generate = true`)**
6. **`auto_scientist_count` (integer, default=3)– _Used only when `auto_generate` is true._**
    
    - The number of Scientist agents to generate if `auto_generate` is true.
    - Mirrors the `agent_count` parameter you have in `/quickstart`.
7. **`auto_include_critic` (boolean, default=true)–  Used only when `auto_generate` is true._**
    
    - Whether to generate a Critic agent automatically if `auto_generate` is true.
    - Mirrors the `include_critic` parameter in `/quickstart`.

**Example Usage**

```
/lab team_meeting agenda:"Explore novel immunotherapy approaches" rounds:4 agent_list:"Principal Investigator, Biologist, Critic"
```

**Behavior**

1. Coordinates the specified (or all) agents in a round-robin or orchestrated conversation.
2. Summarizes at the end, with partial logs posted in Discord and a link to the full transcript.
3. Auto-check if a user tries to start a meeting with no PI. The system can prompt, “Please create a PI agent first.”

---

#### 2I. `/lab end_team_meeting`

**Description**  
Ends an in-progress team meeting within the active session.

**Parameters**

- (Optional) `meeting_id` if multiple are active.

**Example Usage**

```
/lab end_team_meeting
```

**Behavior**

1. Terminates the ongoing conversation.
2. Bot finalizes or marks the transcript as complete.

---

#### 2J. `/lab transcript list`

**Description**  
Lists **meeting transcripts** in the current session.

**Parameters**

- (Optional) filters such as `limit`, `meeting_id`.

**Example Usage**

```
/lab transcript list
```

**Behavior**

1. Shows a list of transcripts from past or current meetings in this session.
2. Each transcript has an ID or short name.

---

#### 2K. `/lab transcript view`

**Description**  
Displays a specific transcript by its ID or reference.

**Parameters**

- **transcript_id** (string, required)

**Example Usage**

```
/lab transcript view transcript_id:12345
```

**Behavior**

1. Fetches the transcript from the backend.
2. Shows a partial or summarized version in Discord, with a link to the full logs.

#### **2L. `/lab reopen`**

**Description**  
**Reopens** a previously ended session, making it the new active session so you can continue working.

**Parameters**

- **session_id** (string or int, required)  
    The ID of the ended session you wish to reopen.
- **confirm** (boolean, optional, default=false)  
    If `true`, confirms you want to un-archive this session.

**Example Usage**

`/lab reopen session_id:1234 confirm:true`

**Behavior**

1. Checks that session 1234 exists and is currently ended/archived.
2. Changes its status to **active**, effectively undoing the “end.”
3. Bot replies: “Session 1234 reopened. Use `/lab agent create` or `/lab team_meeting` to continue.”
4. This reopened session is now the **current active session** (one-at-a-time model).
---

### 3. `/help`

**Description**  
Shows general help or detailed info about a specific command.

**Parameters**

- **command** (string, optional) – if given, displays extended help for that command.

**Example Usage**

```
/help
/help command:"/lab team_meeting"
```

**Behavior**

1. Provides a short usage guide for all major bot commands, or
2. If `command` is specified, shows expanded help with parameters and usage tips.

---

# **Example Usage Flow (One-at-a-Time Sessions)**

> **Note**: `/quickstart` is used alone for a quick, automated setup.  
> Below is an example of **manually** creating and managing a single session at a time with advanced commands:

1. **Start a new session**
    
    ```
    /lab start title:"Project X" is_public:false description:"Exploring AI + Neuroscience"
    ```
    
    - Bot: “Session started. ID = 1234. Use `/lab agent create` to add agents.”
2. **Create a Principal Investigator agent**
    
    ```
    /lab agent create agent_name:"Principal Investigator" expertise:"Neuroscience" goal:"Oversee experiment design" role:"Lead"
    ```
    
    - Bot: “Agent Principal Investigator created.”
3. **Add more Scientist agents**
    
    ```
    /lab agent create agent_name:"ScientistA" expertise:"Machine Learning" goal:"Propose advanced ML approaches" role:"Brainstorming"
    ```
    
    ```
    /lab agent create agent_name:"ScientistB" expertise:"Data Analysis" role:"Provide statistical insights"
    ```
    
4. **(Optional) Create a Critic**
    
    ```
    /lab agent create agent_name:"Critic" role:"Challenge assumptions" goal:"Identify weaknesses or flaws" model:"openai"
    ```
    
5. **Review the agent list**
    
    ```
    /lab agent list
    ```
    
    - Bot: Lists PI, ScientistA, ScientistB, Critic.
6. **Start a team meeting**
    
    ```
    /lab team_meeting agenda:"How can we combine advanced ML with neuroscience data?" rounds:4
    ```
    
    - Bot: Orchestrates 4 rounds of conversation among all 4 agents.
7. **Check transcripts**
    
    ```
    /lab transcript list
    ```
    
    - Bot: Shows transcript IDs for the session’s meetings.
8. **View a transcript**
    
    ```
    /lab transcript view transcript_id:20230302-1
    ```
    
    - Bot: Displays summary/log in Discord with link to full transcript.
9. **End the session**
    
    ```
    /lab end confirm:true public:true
    ```
    
    - Session archived. Marked `public=true`, so it’s visible in your external gallery.
    - Bot: “Session ended. Transcripts remain available for viewing.”

---

## **Revisiting or Copying a Session (Optional)**

Because we’re using a **one-at-a-time** approach, you normally **start** a new session for each new project and **end** the old one. If someone wants to return to a previously ended session (ID=1234):

1. **Option A**: “Reopen” (if you implement `/lab reopen`)
    
    - `/lab reopen session_id:1234`
    - Converts the ended session back to active.
2. **Option B**: “Copy” from old session
    
    - For instance, `/lab copy from_session_id:1234` (a custom command you might implement).
    - Creates a new session (ID=5678) with the same agents, so you can continue working.
    - The original session’s transcripts remain archived.

Either approach ensures you can reference past sessions or continue with the same agents/metadata as needed.

---

### **Closing Notes**

- **Defaults**: Many parameters have defaults (e.g., `agent_count=3`, `include_critic=true`, `is_public=false`).
- **Principal Investigator (PI)**: Always recommended for multi-agent sessions.
- **Transcripts**: Multi-agent discussions (e.g., `/lab team_meeting`) create transcripts accessible via `/lab transcript list` and `/lab transcript view`, _even after the session ends_.
- **Public Sessions**: Appear in your external gallery if `is_public=true`.
- **One-at-a-Time**: This reference follows a simpler model where you **end** one session before starting another. Advanced or parallel session use cases could add commands like `/lab open session_id` for switching, but that’s optional if you want to keep workflows straightforward.

This completes the **TheraLab Virtual** Discord slash command reference, updated to reflect a **one-at-a-time** session workflow with optional session re-use strategies.