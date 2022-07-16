[![Worker](https://github.com/Asi4nn/Shiver-Bot/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/Asi4nn/Shiver-Bot/actions/workflows/python-app.yml)
# Shiver Bot
General use discord bot for small communities

## Major Features

- Birthday Tracker + Announcer
- Message logger (currently disabled)
- Music player (for YouTube)
- A myriad of helpful info commands
- Free Epic games finder

## Usage

You can either download this repo and host with your own bot, or you can add mine:
[Add to your server](https://discord.com/api/oauth2/authorize?client_id=766748400199794718&permissions=8&scope=bot)

Default prefix is ```$``` 

You can get info about all commands with ```$help```

## Development

You can add your information in the ```lib/cogs/general.py``` file if you want
contribution to be shown.

### Cogs

If you make a new cog please update this table with the appropriate info.

Cog Name | File Name | Usage 
--- | --- | ---
Birthday | `birthday.py` | Triggers and commands related to user birthday storage and alerts.
CommandErrorHandler | `command_error.py` | Handles `on_command_error` events.
EpicAlerts | `epic_alerts.py` | Commands relating to finding free game offers on the Epic Games Store.
General | `general.py` | Commands relating to setting and getting information of the bot, setting info about the server for the bot, and additionally contains commands that don't fit well into their own category.
Help | `help.py` | Commands relating to the custom help menu.
Info | `info.py` | Commands to get info about the server or its members.
Log | `log.py` | Listeners for message logging (not in use anymore).
Music | `music.py` | Commands relating to playing music using YouTube.
Reminders | `reminders.py` | Commands relating to 

### Database

I host the Postgres database on Heroku with the bot.

```build.sql``` and ```database.db``` were used for an SQLite database that is no longer in use.

### Some useful commands

- ```PGUSER={user} PGPASSWORD={password} heroku pg:pull DATABASE_URL {local db name} --app shiver-bot```

Copies the deployed database to a local Postgres one of your choice.

- ```heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git```
- ```heroku buildpacks:add https://github.com/xrisk/heroku-opus.git```

Installs FFmpeg and Opus on your Heroku instance.

### Environment Variables

#### .env file

Variable | Usage
--- | ---
TOKEN | Discord bot token
USE_DB | Dev setting to disable the database if needed

### Running the bot

Make sure to have all dependencies in ```requirements.txt``` (use `pip install -r requirements.txt`)
downloaded with at least the python version listed in ```runtime.txt```

Run the ```launcher.py``` file in the venv to run the bot.
