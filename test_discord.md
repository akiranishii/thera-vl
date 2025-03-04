# Discord Bot Testing Guide

This guide provides step-by-step instructions to test all Discord slash commands implemented in the TheraLab Discord bot. Follow these instructions in sequence to validate that all commands function as expected.

## Prerequisites

1. The Discord bot must be added to your server with appropriate permissions
2. You must have the necessary permissions to use slash commands in the server
3. The backend services (database, API) must be running and accessible

## Table of Contents

1. [Basic Commands](#1-basic-commands)
   - [Help Command](#11-help-command)
2. [Session Management](#2-session-management)
   - [Starting a Session](#21-starting-a-session)
   - [Listing Sessions](#22-listing-sessions)
   - [Ending a Session](#23-ending-a-session)
   - [Reopening a Session](#24-reopening-a-session)
3. [Agent Management](#3-agent-management)
   - [Creating Agents](#31-creating-agents)
   - [Listing Agents](#32-listing-agents)
   - [Updating Agents](#33-updating-agents)
   - [Deleting Agents](#34-deleting-agents)
4. [Team Meetings](#4-team-meetings)
   - [Starting a Team Meeting](#41-starting-a-team-meeting)
   - [Ending a Team Meeting](#42-ending-a-team-meeting)
5. [Transcripts](#5-transcripts)
   - [Listing Transcripts](#51-listing-transcripts)
   - [Viewing Transcripts](#52-viewing-transcripts)
6. [Quickstart](#6-quickstart)
   - [Running Quickstart](#61-running-quickstart)
   - [Viewing Results](#62-viewing-results)

## 1. Basic Commands

### 1.1 Help Command

**Command:**
```
/help
```

**Expected output:**
- A message with an embed containing sections for different command categories:
  - 🚀 Quickstart
  - 📋 Lab Session Management
  - 🤖 Agent Management
  - 🗣️ Team Meetings

**Specific command help:**
```
/help command:"quickstart"
```

**Expected output:**
- Detailed information about the quickstart command including all parameters and their descriptions

## 2. Session Management

### 2.1 Starting a Session

**Command:**
```
/lab start title:"Protein Folding Research" description:"Investigating novel approaches to protein folding prediction" is_public:false
```

**Expected output:**
- A "Lab Session Started" embed containing:
  - Session ID (a UUID)
  - Type: Private
  - Status: Active
  - Created by: [Your Username]

### 2.2 Listing Sessions

**Command:**
```
/lab list
```

**Expected output:**
- A "Your Lab Sessions" embed listing your sessions with:
  - Session IDs
  - Titles
  - Status (Active/Ended)
  - Creation dates
  - If no sessions exist, a message saying "You don't have any lab sessions"

### 2.3 Ending a Session

**Command:**
```
/lab end confirm:true public:true
```

**Expected output:**
- A "Lab Session Ended" embed containing:
  - Session ID
  - Title of the ended session
  - Status: Ended
  - Visibility: Public
  - End time

### 2.4 Reopening a Session

**Command:**
```
/lab reopen session_id:"[Session ID from a previous session]"
```

**Expected output:**
- A "Lab Session Reopened" embed containing:
  - Session ID
  - Title of the reopened session
  - Status: Active
  - Reopen time

## 3. Agent Management

### 3.1 Creating Agents

First, make sure you have an active session. If not, create one with `/lab start`.

**Command:**
```
/lab agent_create agent_name:"Principal Investigator" expertise:"Computational biology" goal:"Lead the research team effectively" role:"Team leader" model:"openai"
```

**Expected output:**
- An "Agent Created" embed containing:
  - Agent ID
  - Name: Principal Investigator
  - Expertise: Computational biology
  - Role: Team leader
  - Model: openai

**Create additional agents:**
```
/lab agent_create agent_name:"Molecular Biologist" expertise:"Protein structure analysis" goal:"Identify structural patterns" role:"Domain expert"
```

```
/lab agent_create agent_name:"Critic" expertise:"Research methodology" goal:"Ensure scientific rigor" role:"Critical analysis"
```

### 3.2 Listing Agents

**Command:**
```
/lab agent_list
```

**Expected output:**
- A "Lab Agents" embed listing all created agents with:
  - Agent IDs
  - Names
  - Roles
  - If no agents exist, a message saying "No agents found"

### 3.3 Updating Agents

**Command:**
```
/lab agent_update agent_id:"[Agent ID from previous list]" goal:"New research objective" expertise:"Updated expertise"
```

**Expected output:**
- An "Agent Updated" embed containing:
  - Agent ID
  - Updated fields
  - Previous and new values

### 3.4 Deleting Agents

**Command:**
```
/lab agent_delete agent_id:"[Agent ID from previous list]"
```

**Expected output:**
- An "Agent Deleted" embed containing:
  - Confirmation message
  - Name of the deleted agent

## 4. Team Meetings

### 4.1 Starting a Team Meeting

First, make sure you have an active session with at least a few agents.

**Command:**
```
/lab team_meeting agenda:"Discuss new approaches to protein folding prediction" rounds:3 parallel_meetings:1 live_mode:true
```

**Expected output:**
- A "Team Meeting Started" embed containing:
  - Meeting ID
  - Agenda
  - Number of rounds
  - Participating agents
  - Status: In Progress
  - Live Mode: On

If live_mode is true, you should see messages appearing in the channel as agents respond. Each message should include:
- Agent name
- Role
- Message content
- Round number

### 4.2 Ending a Team Meeting

**Command:**
```
/lab end_team_meeting meeting_id:"[Meeting ID from previous step]"
```

**Expected output:**
- A "Team Meeting Ended" embed containing:
  - Meeting ID
  - End time
  - Summary of participation (number of messages, rounds completed)

## 5. Transcripts

### 5.1 Listing Transcripts

**Command:**
```
/lab transcript_list
```

**Expected output:**
- A "Meeting Transcripts" embed listing available transcripts with:
  - Meeting IDs
  - Meeting titles/agendas
  - Creation dates
  - Number of messages
  - If no transcripts exist, a message saying "No transcripts found"

### 5.2 Viewing Transcripts

**Command:**
```
/lab transcript_view meeting_id:"[Meeting ID from previous list]"
```

**Expected output:**
- A "Meeting Transcript" embed containing:
  - Meeting ID
  - Meeting agenda
  - A chronological list of messages with:
    - Agent names
    - Timestamps
    - Message content
  
**Filter by round:**
```
/lab transcript_view meeting_id:"[Meeting ID]" round_number:2
```

**Expected output:**
- Only messages from round 2

**Filter by agent:**
```
/lab transcript_view meeting_id:"[Meeting ID]" agent_name:"Principal Investigator"
```

**Expected output:**
- Only messages from the Principal Investigator

## 6. Quickstart

### 6.1 Running Quickstart

The quickstart command combines multiple steps (session creation, agent creation, and team meeting) into a single command.

**Command:**
```
/quickstart topic:"Developing new CRISPR delivery mechanisms" agent_count:3 include_critic:true public:false live_mode:true
```

**Expected output:**
- A "Quickstart Complete" embed containing:
  - Session Details:
    - Session ID
    - Privacy: Private
    - Agents: 5 total (1 Principal Investigator, 3 Scientists, 1 Critic)
  - Meeting:
    - Meeting ID
    - Rounds: 3
    - Status: In Progress
    - Live Mode: On
  - View Progress:
    - Instructions to use `/lab transcript_view [Meeting ID]`

If live_mode is true, you should see a series of messages in the channel as the agents discuss the topic, including:
1. A welcome message from the Principal Investigator
2. Introductions from each Scientist agent
3. Initial thoughts on the topic
4. Responses to each other's ideas
5. Summary or conclusions

### 6.2 Viewing Results

After the discussion completes or while it's in progress, check the transcript:

**Command:**
```
/lab transcript_view meeting_id:"[Meeting ID from quickstart]"
```

**Expected output:**
- The complete transcript of the agent conversation

## Troubleshooting

If any command fails:
1. Check that the bot is online and has proper permissions
2. Verify that you have an active session when required
3. Make sure you're providing valid IDs when referencing sessions, agents, or meetings
4. Check the server logs for any error messages

## Expected Error Messages

The following are normal error responses in certain situations:

1. When trying to create an agent without an active session:
   - "You don't have an active session. Start one with `/lab start` first."

2. When trying to end a non-existent meeting:
   - "Meeting not found or already ended."

3. When providing an invalid session ID:
   - "Invalid session ID or session not found." 