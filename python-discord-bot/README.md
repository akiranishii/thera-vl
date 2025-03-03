# Thera-VL Discord Bot

This Discord bot integrates with the Thera-VL web application to allow users to create and manage therapeutic sessions through Discord.

## Features

- Create and manage therapy sessions
- Interact with AI therapists
- Access session history
- Receive real-time transcripts

## Installation

1. Clone the repository
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the main `.env.example` to `.env.local` at the root level and fill in the required environment variables:

```
DISCORD_TOKEN=your_discord_bot_token
APPLICATION_ID=your_discord_application_id
API_BASE_URL=http://localhost:3000  # Or your deployed app URL
OPENAI_API_KEY=your_openai_api_key
```

4. Alternatively, you can create a `local_env.yml` file in the `python-discord-bot` directory with the following format:

```yaml
DISCORD_TOKEN: "your_discord_bot_token"
APPLICATION_ID: "your_discord_application_id"
API_BASE_URL: "http://localhost:3000"
OPENAI_API_KEY: "your_openai_api_key"
```

## Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" tab and click "Add Bot"
4. Under the "Privileged Gateway Intents" section, enable:
   - Message Content Intent
   - Server Members Intent
5. Copy the bot token and add it to your environment variables
6. Go to the "OAuth2" tab, then "URL Generator"
7. Select the following scopes:
   - bot
   - applications.commands
8. Select the following bot permissions:
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History
   - Use Slash Commands
9. Copy the generated URL and use it to invite the bot to your server

## Running the Bot

```bash
python main.py
```

## Available Commands

### Session Management

- `/start [title] [description] [public]` - Start a new therapy session
  - `title` - Title of your session
  - `description` (optional) - Brief description of what you'd like to discuss
  - `public` (optional) - Whether the session should be public (default: false)
  
- `/end` - End your current active session

Additional commands will be implemented in future updates.

## Development

The bot is structured as follows:

- `main.py` - The entry point for the bot
- `config.py` - Configuration management
- `db_client.py` - Client for interacting with the web app's API
- `commands/` - Command modules organized by functionality
  - `session_commands.py` - Commands for managing sessions
  - (Additional command modules to be added)

To add new commands:

1. Create a new file in the `commands` directory or add to an existing one
2. Create a new class that inherits from `commands.Cog`
3. Add your command methods using the `@app_commands.command()` decorator
4. Register your command in the `INITIAL_EXTENSIONS` list in `main.py`

## Troubleshooting

Check the `bot.log` file for detailed error messages.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 