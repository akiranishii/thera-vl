```markdown
# Discord Bot Integration with LLM APIs

This documentation provides a step-by-step guide for integrating **Discord bots** with various Large Language Model (LLM) providers. We'll walk through:

- Setting up a Discord bot
- Configuring environment variables
- Using an LLM wrapper (like Mistral, OpenAI, or Claude)
- Handling conversation history
- Responding to user messages and commands
- General best practices for Discord bot development

> **Note**: All examples here are purely illustrative. You are free to adapt them for any LLM provider or for your own specific use cases.

---

## Table of Contents

1. [Overview](#overview)  
2. [Prerequisites](#prerequisites)  
3. [Project Structure](#project-structure)  
4. [Environment Variables](#environment-variables)  
5. [Discord Bot Setup](#discord-bot-setup)  
6. [Mistral Example Integration](#mistral-example-integration)  
7. [OpenAI Example Integration](#openai-example-integration)  
8. [Anthropic (Claude) Example Integration](#anthropic-claude-example-integration)  
9. [Discord Bot Code Explanation](#discord-bot-code-explanation)  
   - [Main Bot File](#main-bot-file)  
   - [Agent File (LLM Logic)](#agent-file-llm-logic)  
10. [Commands & Interactions](#commands--interactions)  
    - [Text-based Commands (Prefix Commands)](#text-based-commands-prefix-commands)  
    - [Slash Commands (Interactions)](#slash-commands-interactions)  
11. [Best Practices & Tips](#best-practices--tips)  
12. [Additional Resources](#additional-resources)

---

## Overview

Discord bots are automated applications that connect to Discord to perform a wide variety of tasks, such as moderating servers, playing music, or — in our case — generating AI-based responses to user messages. By combining Discord’s robust APIs with modern Large Language Models, you can create a powerful AI assistant that users can interact with directly in your Discord server.

---

## Prerequisites

- **Python 3.9+**  
- A **Discord Developer account** (to create and manage your bot)
- A basic understanding of **Python** and **asynchronous programming** (using `async/await`)
- Familiarity with **pip** or **venv** for managing dependencies
- **LLM API keys** for whichever provider(s) you plan to use (e.g., Mistral, OpenAI, Anthropic, etc.)

---

## Project Structure

A typical Python project might look like this:

```
my_discord_bot/
├── .env
├── bot.py
├── agent.py
├── requirements.txt
└── README.md
```

- **`.env`**: Holds environment variables (Discord token, API keys, etc.).  
- **`bot.py`**: Main script that starts the Discord bot and includes event handling.  
- **`agent.py`**: Contains logic for interacting with the LLM APIs.  
- **`requirements.txt`**: Lists Python dependencies.

---

## Environment Variables

Create a file named `.env` (or store them securely in your hosting environment) to hold your keys:

```
DISCORD_TOKEN=your_discord_bot_token_here
MISTRAL_API_KEY=your_mistral_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

> **Warning**: Never commit `.env` to version control. Treat all tokens and secrets as private.

---

## Discord Bot Setup

1. **Create an application** in the [Discord Developer Portal](https://discord.com/developers/applications).
2. **Add a Bot user**: In your application settings, go to **Bot** → **Add Bot**.
3. **Copy your Bot Token** from the **Bot** section. **Never** share this token publicly.
4. **Invite the Bot to your server**: Go to the **OAuth2 → URL Generator**, select the `bot` scope (and optional `applications.commands` if using slash commands). Specify the permissions your bot needs, then use the generated URL to invite the bot to your guild (server).

---

## Mistral Example Integration

Below is an example using the **Mistral** LLM. We use the [mistralai](https://pypi.org/project/mistralai/) client (hypothetical) to send chat completions.

```python
# agent_mistral.py

import os
import discord
from mistralai import Mistral

SYSTEM_PROMPT = "You are a helpful assistant."
MISTRAL_MODEL = "mistral-large-latest"
MAX_HISTORY_LENGTH = 10

class MistralAgent:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.client = Mistral(api_key=self.api_key)
        self.channel_history = {}

    async def run(self, message: discord.Message):
        channel_id = message.channel.id
        
        # Initialize conversation history
        if channel_id not in self.channel_history:
            self.channel_history[channel_id] = []
        
        # Track user message in history
        self.channel_history[channel_id].append({
            "role": "user",
            "content": message.content
        })
        
        # Compose final payload for Mistral
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        history = self.channel_history[channel_id][-MAX_HISTORY_LENGTH:]
        messages.extend(history)
        
        # Fetch LLM response
        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
        )
        
        ai_response = response.choices[0].message.content

        # Store AI response in history
        self.channel_history[channel_id].append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Trim history if too large
        if len(self.channel_history[channel_id]) > MAX_HISTORY_LENGTH * 2:
            self.channel_history[channel_id] = self.channel_history[channel_id][-MAX_HISTORY_LENGTH:]
        
        return ai_response

    async def run_with_text(self, text: str):
        """
        Process text input without keeping conversation history.
        Great for ephemeral or slash command usage.
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]

        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
        )
        return response.choices[0].message.content
```

- **`run`**: Maintains conversation history tied to the Discord channel.  
- **`run_with_text`**: Accepts raw text (no conversation context).

---

## OpenAI Example Integration

Suppose you want to use [OpenAI’s GPT models](https://platform.openai.com/docs/introduction). You could write an `agent_openai.py` like this:

```python
# agent_openai.py

import os
import discord
import openai

SYSTEM_PROMPT = "You are a helpful assistant."
OPENAI_MODEL = "gpt-3.5-turbo"
MAX_HISTORY_LENGTH = 10

class OpenAIAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.channel_history = {}

    async def run(self, message: discord.Message):
        channel_id = message.channel.id
        
        if channel_id not in self.channel_history:
            self.channel_history[channel_id] = []
        
        self.channel_history[channel_id].append({
            "role": "user",
            "content": message.content
        })
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        history = self.channel_history[channel_id][-MAX_HISTORY_LENGTH:]
        messages.extend(history)
        
        # API call
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages
        )
        ai_response = response.choices[0].message.content
        
        self.channel_history[channel_id].append({
            "role": "assistant",
            "content": ai_response
        })

        if len(self.channel_history[channel_id]) > MAX_HISTORY_LENGTH * 2:
            self.channel_history[channel_id] = self.channel_history[channel_id][-MAX_HISTORY_LENGTH:]
        
        return ai_response

    async def run_with_text(self, text: str):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ]
        
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages
        )
        return response.choices[0].message.content
```

---

## Anthropic (Claude) Example Integration

For [Anthropic (Claude)](https://docs.anthropic.com/claude/docs), the setup can be similar:

```python
# agent_claude.py

import os
import discord
import anthropic

SYSTEM_PROMPT = "You are a helpful assistant."
CLAUDE_MODEL = "claude-2"
MAX_HISTORY_LENGTH = 10

class ClaudeAgent:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.channel_history = {}

    async def run(self, message: discord.Message):
        channel_id = message.channel.id
        
        if channel_id not in self.channel_history:
            self.channel_history[channel_id] = []
        
        self.channel_history[channel_id].append({
            "role": "user",
            "content": message.content
        })
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        history = self.channel_history[channel_id][-MAX_HISTORY_LENGTH:]
        messages.extend(history)

        # Convert system/user/assistant roles to the Anthropic format if needed
        # For simplicity, let's assume we handle that logic here:
        anthropic_prompt = ...
        # Build your Anthropics Prompt from messages

        response = self.client.completions.create(
            model=CLAUDE_MODEL,
            max_tokens_to_sample=1024,
            prompt=anthropic_prompt,
        )

        # Extract the content from the response
        ai_response = response.completion

        self.channel_history[channel_id].append({
            "role": "assistant",
            "content": ai_response
        })

        if len(self.channel_history[channel_id]) > MAX_HISTORY_LENGTH * 2:
            self.channel_history[channel_id] = self.channel_history[channel_id][-MAX_HISTORY_LENGTH:]
        
        return ai_response

    async def run_with_text(self, text: str):
        """
        No conversation context.
        """
        # Build the prompt with system + user
        anthropic_prompt = ...
        response = self.client.completions.create(
            model=CLAUDE_MODEL,
            max_tokens_to_sample=1024,
            prompt=anthropic_prompt,
        )
        return response.completion
```

---

## Discord Bot Code Explanation

Below is a **sample** `bot.py` that uses **discord.py** (or `py-cord`) to connect your agent to Discord. You can adapt it to whichever agent you prefer (MistralAgent, OpenAIAgent, ClaudeAgent, etc.).

### Main Bot File

```python
# bot.py

import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv

# Choose your agent import here:
# from agent_mistral import MistralAgent
# from agent_openai import OpenAIAgent
# from agent_claude import ClaudeAgent

load_dotenv()  # Load secrets from .env
TOKEN = os.getenv("DISCORD_TOKEN")

PREFIX = "!"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Example using Mistral
agent = MistralAgent()

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to Discord!")

@bot.event
async def on_message(message: discord.Message):
    # Skip messages from bots or if it starts with "!" (our command prefix)
    # so we don’t handle them twice
    if message.author.bot or message.content.startswith(PREFIX):
        return

    # Let the bot process commands (important!)
    await bot.process_commands(message)

    # Send user message to the LLM agent
    logger.info(f"Processing message from {message.author}: {message.content}")
    response = await agent.run(message)

    # Reply to the user with the LLM's response
    await message.reply(response)


@bot.command(name="ping", help="Basic ping command")
async def ping_command(ctx, *, arg=None):
    if arg:
        await ctx.send(f"Pong! Argument: {arg}")
    else:
        await ctx.send("Pong!")

@bot.command(name="ask", help="Query the LLM without conversation context")
async def ask_command(ctx, *, question=None):
    if not question:
        await ctx.send("Please provide a question.")
        return
    response = await agent.run_with_text(question)
    await ctx.send(response)

# Start the bot
bot.run(TOKEN)
```

**Key Points**:

- **`on_ready`** fires once the bot successfully connects to Discord.  
- **`on_message`** intercepts all incoming messages. We skip bot messages and those starting with our prefix to avoid duplicates.  
- We call `agent.run(message)` to pass the user’s message to the LLM and then reply.  
- We have two example prefix commands: `!ping` and `!ask`.  

---

### Agent File (LLM Logic)

Depending on the LLM you want, you can place the agent logic in a separate file (like `agent.py` or `agent_openai.py`). This keeps your code organized. For brevity, the code above references the agent class with the `run` and `run_with_text` methods that you’d define in one of the example agent files shown earlier.

---

## Commands & Interactions

### Text-based Commands (Prefix Commands)

- **Prefix commands** are traditional commands triggered by a prefix (`!ping`, `!ask`, etc.).  
- We used `discord.ext.commands.Bot` with `command_prefix=PREFIX`.  
- Each command is decorated with `@bot.command(...)`.  

> **Pros**: Familiar approach, works in most libraries.  
> **Cons**: Doesn’t leverage Discord’s slash command UI/auto-complete.

### Slash Commands (Interactions)

Alternatively, use the [**Application Commands** (slash commands)](https://discord.com/developers/docs/interactions/application-commands#slash-commands). For slash commands, you’ll need to:

1. Enable the `applications.commands` scope in your bot invite.  
2. Either register commands via code (using something like `@bot.tree.command()` in `py-cord`/`discord.py` 2.x) or create them via Discord’s Application Commands API.  
3. Handle `interaction` events and respond accordingly.

**Example Slash Command** registration JSON:
```json
{
  "name": "ask",
  "type": 1,
  "description": "Ask the AI assistant a question",
  "options": [
    {
      "name": "question",
      "description": "The question to ask",
      "type": 3,
      "required": true
    }
  ]
}
```
Where `type: 1` indicates a **CHAT_INPUT** slash command.

In code, a minimal example (using newer `discord.py` or `py-cord` slash command support) might look like:

```python
@bot.tree.command(name="ask", description="Ask the AI assistant a question")
async def ask_command(interaction: discord.Interaction, question: str):
    response = await agent.run_with_text(question)
    await interaction.response.send_message(response)
```

> **Note**: This approach may differ based on your library’s version. Check the docs for your specific library (e.g., `discord.py 2.0+`, `py-cord`, or `nextcord`).

---

## Best Practices & Tips

1. **Always protect your tokens**. Store them in environment variables or a secure vault.  
2. **Handle rate limits**. Libraries like `discord.py` automatically queue requests to avoid hitting [Discord’s rate limits](https://discord.com/developers/docs/topics/rate-limits).  
3. **Use gateway intents properly**. If you need to read message content, enable the **Message Content Intent** in the Developer Portal. This is **privileged** for bots in 100+ servers.  
4. **Split your logic**. Keep your LLM logic separate from your Discord event logic. This makes your code cleaner and more modular.  
5. **Conversation history management**. Storing entire conversation history can be memory-intensive. Limit the number of recent messages or store them in a lightweight database.  
6. **Error handling**. Wrap your LLM calls in try/except blocks to catch connectivity issues or API errors.  
7. **Be mindful of user privacy**. Don’t log entire messages with sensitive info. If you must store logs, anonymize them.  
8. **Performance**. LLM calls can be expensive and sometimes slow. Consider adding caching or rate-limiting if your bot grows popular.  
9. **Testing**. Test your bot in a private server before deploying to a large community.  

---

## Additional Resources

- **[Discord Developer Portal](https://discord.com/developers/docs/intro)**
- **[discord.py Library Docs](https://discordpy.readthedocs.io/en/stable/)** or relevant forks (`py-cord`, `nextcord`, etc.)
- **[Mistral AI (Hypothetical) Docs](#)** (depending on the library you use)
- **[OpenAI Docs](https://platform.openai.com/docs/introduction)**
- **[Anthropic (Claude) Docs](https://docs.anthropic.com/claude/docs)**
- **[dotenv](https://pypi.org/project/python-dotenv/)** for environment variable handling

---

## Conclusion

With these examples, you should have a solid foundation to:

- Set up a basic Discord bot
- Interact with various LLM APIs for AI-powered chat
- Manage conversation history per-channel
- Extend your bot with commands, slash commands, or advanced features like embedded messages, file attachments, and more

Feel free to customize the conversation logic, add slash commands, or integrate other AI services. By following best practices and using environment variables correctly, you can build a secure and feature-rich AI assistant for your Discord community. Good luck!
```