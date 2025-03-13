# Thera VL – Multi-Agent Collaboration, Context-Tracking, and Data Augmentation

# Demo Video

[Watch the Demo Video on Loom](https://www.loom.com/share/566403785fef4f2785e300bfc5880bd2?sid=18391ec7-1bde-4dde-aa1e-dbb754a466a1)


## Additional References

- [Context-Tracking Framework Documentation](https://github.com/thera-core/context-framework)
- [Data Augmentation Framework Documentation](https://github.com/thera-core/data-augmentation-framework)
- [TheraLab Orchestrator & Discord Bot Scripts](./python-discord-bot/)

Welcome to **Thera VL** (Thera Virtual Lab), a multi-agent research environment that integrates a **Discord Bot**, a **Context-Tracking Framework**, and a **Data Augmentation Framework** to enable dynamic, AI-driven workflows. This README focuses on how these major components fit together technically and how you can use them for your multi-agent sessions.

---

## Overview

Thera VL is structured around three core ideas:

1. **Multi-Agent Workflow & Discord Bot**  
   - A Python-based Discord bot for user interactions, slash commands, and real-time AI multi-agent sessions.
   - Orchestration logic that handles multiple AI agents, user commands (`/startsession`, `/lab`, etc.), and conversation transcripts.

2. **Context-Tracking Framework**  
   - A lightweight library for attaching and retrieving metadata on data structures (e.g., columns, rows, HPC transforms).
   - Acts as an external “memory” that is particularly valuable for large or iterative LLM-based tasks.

3. **Data Augmentation Framework**  
   - Specialized augmentation logic to enrich or transform data (e.g., PubMed lookups, HPC-based transformations).
   - After transformations, it invokes the context framework to store logs, provenance, or additional metadata.

Thera VL orchestrates these layers. In a typical usage flow:

1. A user in Discord invokes a slash command (e.g., `/startlab` or `/augmentdata`).  
2. The Thera VL Discord Bot routes the request to an appropriate agent or function.  
3. If data transformations are requested, the **Data Augmentation Framework** is called.  
4. That framework uses the **Context-Tracking Framework** to attach logs or metadata.  
5. Results flow back up to the user, who sees the outcome in Discord (including multi-agent insights or additional data references).

---

## Repository Layout

Although you may see them combined in a monorepo or submodules, conceptually these are three repos:

1. **`akiranishii/thera-vl`** (this product layer, including the Discord Bot and multi-agent orchestration)
2. **`thera-core/context-framework`** (generic context-tracking library)
3. **`thera-core/data-augmentation-framework`** (specialized transformation and augmentation code)

### In This Repo (TheraLab)

- **Discord Bot** code for user slash commands
- **Multi-agent orchestrator** (facilitates conversation among agents)
- **Digital journal** / logging for transcripts and final summaries  
- **Integration** with the two lower-level frameworks

### Context-Tracking Framework

- **Attaches context** (metadata) to in-memory or distributed data structures
- **Adapters** for Pandas, Spark, or domain objects
- **Store** options: in-memory, Redis, DB-based
- **Flexible** enough to serve as “long-term memory” for LLM-based flows

For more details, see [Context-Tracking Framework](https://github.com/thera-core/context-framework).

### Data Augmentation Framework

- **Specialized logic** to fetch data from external sources (PubMed, HPC transforms, etc.)
- **Integrates** with the context framework to store transformation logs
- **Concurrency** or HPC patterns for large-scale tasks

For more details, see [Data Augmentation Framework](https://github.com/thera-core/data-augmentation-framework).

---

## How They Work Together

1. **User** initiates action in Discord  
   E.g. `/startlab`, `/uploadfile`, or `/augmentdata`.

2. **TheraLab** (Discord Bot + Orchestrator) receives the command  
   - Checks if a multi-agent session is running
   - Might pass a request to a dedicated agent or function

3. **Data Augmentation** invoked for advanced transformations  
   - The augmentation code updates or creates data structures
   - Immediately uses the **Context-Tracking** library to attach logs, provenance, or HPC metadata

4. **Context-Tracking** is the persistent “memory”  
   - Agents can “call an API” to fetch details from these contexts (especially relevant for large data or LLM-limited context windows)

5. **Results** flow back to the orchestrator, which updates transcripts and the digital journal  
   - The user sees final or intermediate results in Discord
   - Each step is logged for future reference, enabling robust multi-round or multi-agent research flows

---

## Using the Discord Bot

### Prerequisites

- **Python 3.9+**  
- A **Discord application** (registered in the [Discord Developer Portal](https://discord.com/developers)).
- Environment variables set for the bot to know your **API_BASE_URL** (pointing to TheraLab’s server if you have a separate backend).

### Setup

1. **Install Dependencies**:  
   ```bash
   cd python-discord-bot
   pip install -r requirements.txt
   ```

2. **Set Environment Variables** (e.g. in `.env`):
   ```bash
   DISCORD_BOT_TOKEN="your_discord_bot_token"
   APPLICATION_ID="your_discord_application_id"
   API_BASE_URL="http://localhost:3000/api"  # or your deployment
   # ... plus any keys for external LLMs (OpenAI, Anthropic, Mistral) ...
   ```

3. **Run the Bot**:
   ```bash
   python main.py
   ```

4. **Invite the Bot**  
   - In the Developer Portal → OAuth2 → URL Generator  
   - Select `bot` + `applications.commands`  
   - Invite the bot to your server.

### Slash Commands

Typical slash commands:

- `/startsession` (or `/lab start`)  
  Initialize a multi-agent session or “lab,” letting you attach data or start orchestrating agents.

- `/lab agent_create ...`  
  Create a new AI agent with specified roles or goals.

- `/lab agent_list`  
  List existing agents in the session.

- `/lab team_meeting ...`  
  Start a multi-agent conversation (a meeting). The orchestrator handles each agent’s turn.

- `/lab end_team_meeting`  
  Conclude the meeting. Optionally generate a summary or store logs.

- `/augmentdata ...` (or some similar command)  
  Tells a data-augmenting agent to fetch references from PubMed or perform HPC transforms. Under the hood, it calls the **Data Augmentation Framework**.

### Conversation & Context

- The orchestrator can store partial transcripts in a local DB or with context data.  
- If an agent or user wants to recall something that happened 50 messages ago, the **context-framework** can retrieve the relevant logs or metadata by key (no LLM forgetting).

---

## Context Management

### Installation (Context Framework)

```bash
pip install context-framework
```

(Or see the [repo docs](https://github.com/thera-core/context-framework) for advanced setups.)

### Basic Usage in an Agent or Script

```python
from context_framework.context_store import InMemoryContextStore
from context_framework.adapters.pandas_adapter import PandasContextAdapter
import pandas as pd

# Create data + store
df = pd.DataFrame({"GeneSymbol": ["BRCA1", "TP53"], "Expression": [12.3, 8.4]})
store = InMemoryContextStore()

# Wrap with a PandasContextAdapter
adapter = PandasContextAdapter(df, context_store=store)

# Add context to "GeneSymbol" column
adapter.add_context(("column", "GeneSymbol"), {"source": "PubMed", "description": "Gene symbol column"})

# Retrieve later
metadata = adapter.get_context(("column", "GeneSymbol"))
print(metadata)
# -> {"source": "PubMed", "description": "Gene symbol column"}
```

**LLMs** or multi-agent code can query these stored keys to re-load relevant data or prompts that aren’t in their immediate chat buffer.

---

## Data Augmentation Framework (WORK IN PROGRESS)

### Installation

```bash
pip install data-augmentation-framework
```
(Or see [GitHub repo](https://github.com/thera-core/data-augmentation-framework).)

### Example

**PubMedAugmenter** or HPC-based transformations might:

1. Accept a data structure (like a Pandas DataFrame).  
2. Look up references for a given gene.  
3. Call `adapter.add_context(...)` to store logs about the transformation.  
4. Return the augmented data to the orchestrator.

```python
from data_augmentation_framework.augmenters import PubMedAugmenter
from context_framework.adapters.pandas_adapter import PandasContextAdapter

# Suppose we already have df + store + adapter
augmenter = PubMedAugmenter()

# Augment the "GeneSymbol" column with references
augmenter.augment_column(adapter, "GeneSymbol")

# The augmenter calls adapter.add_context(("column", "GeneSymbol"), {...})
# to store provenance details, e.g. PubMed IDs used, date, etc.
```

Now the orchestrator (TheraLab) or an agent can retrieve these references from context without losing them over a long conversation.

---

## Overall Vision

1. **Discord Bot** is the user interface.  
   - Slash commands or channel messages start new sessions, create or update agents, and manage data transformations.

2. **Multi-Agent Orchestrator** handles the logic of who speaks next, merges final summaries, and logs events into a “digital journal.”

3. **Data Augmentation** gets invoked for domain-specific tasks—pulling in external data or performing HPC transformations.

4. **Context Framework** ensures these transformations, transcripts, and partial logs never vanish due to LLM context limits or session restarts.

In summary, Thera VL aims to provide **end-to-end AI-human collaborative research**:

- **User**: “Hey bot, please fetch references for these genes and run HPC normalization.”  
- **Multi-Agent Orchestrator**: Figures out which “agent” handles the request.  
- **Data Augmentation**: Actually does the transform, logs it.  
- **Context-Tracking**: Keeps track of all these logs, so even if your LLM’s window is exceeded, you still have a systematic memory of transformations and conversation threads.

---

## Next Steps & Customization

- **Add More Agents**: Write new Python agent classes or slash commands that do specialized tasks.
- **Extend Context Adapters**: If you have a special data structure (Spark, HPC arrays), build a custom adapter to store row- or partition-level context.
- **Custom Augmenters**: Create domain-specific transformations or HPC tasks under the data-augmentation-framework, ensuring each step calls the context framework to log metadata.

---


For questions or issues, please open an issue in the relevant repository or email akira.nishii@thera-ai.com

Happy hacking with **Thera VL**!