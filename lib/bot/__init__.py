from discord.ext.commands import Bot as BaseBot
import os

PREFIX = '/'
OWNER_IDS = [164144088818515968]
COGS = []

for filename in os.listdir('./lib/cogs'):
    if filename.endswith('.py'):
        COGS.append(f'lib.cogs.{filename[:-3]}')


class Bot(BaseBot):
    def __init__(self):
        self.ready = False
        self.prefix = PREFIX
        self.guild = None

        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS)

    def run(self):
        with open('lib/bot/TOKEN.txt', 'r', encoding="utf-8") as token:
            self.token = token.read()

        super().run(self.token, reconnect=True)

    async def on_connect(self):
        print("Logged in as {0.user}".format(self))

    async def on_disconnect(self):
        print("Bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == 'on_command_error':
            print("Something went wrong")
        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            await ctx.send("Command not found")
        elif hasattr(exc, 'original'):
            raise exc.original
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.guild = self.get_guild(636310389797290024)
            for cog in COGS:
                self.load_extension(cog)
                print(f'Loaded cog: {cog}')
            print("Bot is ready")
        else:
            print("Bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
