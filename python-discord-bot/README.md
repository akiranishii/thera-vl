# Thera VL Discord Bot

A Discord bot for Thera Virtual Lab that facilitates multi-agent research and brainstorming sessions in Discord channels.

## Features

- Create and manage research and brainstorming sessions
- Define AI agents with different roles and personalities
- Run individual meetings with agents
- Conduct multi-agent brainstorming sessions
- View session transcripts
- Support for parallel meetings

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- A Discord account with a registered application and bot
- API keys for at least one LLM provider (OpenAI, Anthropic, or Mistral)
- Supabase database credentials

### Installation

1. Clone the repository (if not already included in your project)

2. Install dependencies:
   ```bash
   cd python-discord-bot
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   
   Ensure the following variables are set in your `.env.local` file in the project root:
   
   ```
   # Discord Bot Token
   DISCORD_TOKEN=your_discord_bot_token_here
   
   # Supabase Credentials
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
   
   # LLM API Keys (at least one is required)
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   MISTRAL_API_KEY=your_mistral_api_key_here
   ```

4. Run the bot:
   ```bash
   python main.py
   ```

### Discord Bot Setup

1. Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)

2. Add a bot to your application:
   - Go to the "Bot" tab and click "Add Bot"
   - Under "Privileged Gateway Intents", enable:
     - Presence Intent
     - Server Members Intent
     - Message Content Intent

3. Get your bot token:
   - Click "Reset Token" if needed
   - Copy the token and add it to your `.env.local` file

4. Invite the bot to your server:
   - Go to OAuth2 > URL Generator
   - Select the "bot" and "applications.commands" scopes
   - Select required permissions (at minimum: Read Messages, Send Messages, Use Slash Commands)
   - Copy and open the generated URL in your browser
   - Select your server and authorize the bot

## Usage

Once the bot is running and has joined your server, you can interact with it using the following commands:

- `/ping`: Check if the bot is responsive
- `/hello`: Get a greeting from the bot

More commands will be added as they are implemented.

## Project Structure

- `main.py`: Main bot entry point and event handlers
- `config.py`: Configuration settings and environment variable handling
- `db_client.py`: Database client for interacting with Supabase
- `requirements.txt`: Python dependencies

## Development

To contribute or extend the bot:

1. Create command files in a `commands/` directory
2. Add the commands to the bot in `main.py`
3. Update this README with new commands and features

## Troubleshooting

- **Bot not responding**: Check that the bot is running and has the correct permissions in your Discord server
- **Database connection issues**: Verify your Supabase credentials and ensure the tables exist
- **LLM API errors**: Check that your API keys are valid and have sufficient quota 