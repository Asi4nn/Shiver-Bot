[![Worker](https://github.com/Asi4nn/Shiver-Bot/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/Asi4nn/Shiver-Bot/actions/workflows/python-app.yml)
# Shiver Bot
General use discord bot for small communities

## Major Features

- Birthday Tracker + Announcer
- Message logger (currently disabled)
- Music player (for YouTube)
- A myriad of helpful info commands

## Usage

You can either download this repo and host with your own bot, or you can add mine:
[Add to your server](https://discord.com/api/oauth2/authorize?client_id=766748400199794718&permissions=8&scope=bot)

Default prefex is ```$``` 

You can get info about all commands with ```$help```

## Contributing

You can add your information in the ```lib/cogs/general.py``` file if you want
contribution to be shown.

### Database

I host the Postgres database on Heroku with the bot.

```build.sql``` and ```database.db``` were used for an SQLite database that is no longer in use.

#### Some useful commands:
- ```git pull heroku main```

Pulls the remote repository from Heroku to current branch

- ```git push heroku {branch}:main```

Push ```branch``` to deploy to Heroku, currently using a private ```deployment```
branch to store the ```TOKEN.txt```


NOTE: Token might be changed to an environment var to ease the deployment process

- ```PGUSER={user} PGPASSWORD={password} heroku pg:pull DATABASE_URL {local db name} --app shiver-bot```

Copies the deployed database to a local Postgres one of your choice

- ```heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git```
- ```heroku buildpacks:add https://github.com/xrisk/heroku-opus.git```

Installs FFmpeg and Opus on your Heroku instance

### Copying the repo

Make sure you make a file ```TOKEN.txt``` in  ```lib/bot``` 
with your own Discord bot token if you plan on hosting it yourself

### Running the bot

Make sure to have all dependencies in ```requirements.txt``` 
downloaded with at least the python version listed in ```runtime.txt```

Run the ```launcher.py``` file in the venv to run the bot, a ```run.bat``` file is 
also provided for convenience.
