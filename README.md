# Discord Reaction Role Manager

A simple command-line tool that adds or removes a Discord role from users who reacted to a specific Discord message.

The script runs once, completes the requested action, and then stops. It does not run as a continuous Discord bot.

## Features

- Add a role to users who reacted to a message
- Remove a role from users who reacted to a message
- Runs from the command line
- Uses environment variables for Discord credentials
- Logs users who were processed
- Skips users who already have the role when using ADD
- Skips users who do not have the role when using REMOVE
- Handles Discord API errors without crashing

## Requirements

- Python 3.10 or newer
- A Discord bot
- A Discord server where you have permission to manage roles

## Installation

Clone this repository:

```bash
git clone https://github.com/YOUR-USERNAME/discord-reaction-role-manager.git
cd discord-reaction-role-manager
