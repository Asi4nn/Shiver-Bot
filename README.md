# Shiver Bot
General use discord bot

## Usage

You can either download this repo and host with your own bot, or you can add mine:
[Add to your server](https://discord.com/api/oauth2/authorize?client_id=766748400199794718&permissions=8&scope=bot)

Default prefex is ```$``` 

You can get info about all commands with ```$help```

## Modifying

You can add your information in the ```lib/cogs/general.py``` file if you want
contribution to be shown.

### Database

I host the Postgres database on Heroku with the bot.

```build.sql``` and ```database.db``` were used for an SQLite database that is no longer in use.

#### Some useful scripts:
- ```PGUSER={user} PGPASSWORD={password} heroku pg:pull DATABASE_URL {local db name} --app shiver-bot```

Copies the deployed database to a local Postgres one of your choice

### Copying the repo

Make sure you make a file ```TOKEN.txt``` in  ```lib/bot``` with your own Discord bot token if you plan on hosting it yourself
