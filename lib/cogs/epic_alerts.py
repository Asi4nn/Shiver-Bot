from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command
from datetime import datetime

from epicstore_api.api import EpicGamesStoreAPI
import json

from pytz import timezone, utc

epic_api = EpicGamesStoreAPI()


class EpicAlerts(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="epic_free", brief="Lists this week's free game(s) from the Epic Games Store")
    async def epic_free(self, ctx):
        games = epic_api.get_free_games()["data"]["Catalog"]["searchStore"]["elements"]
        print(json.dumps(games, indent=4))

        for game in games:
            if game["price"]["totalPrice"]["discountPrice"] == 0 and game["price"]["totalPrice"]["originalPrice"] > 0:
                embed = Embed(title=game["title"], description=game["description"], colour=ctx.author.color)
                image_url = None
                for image in game["keyImages"]:
                    if image["type"] == "Thumbnail":
                        image_url = image["url"]
                        break
                if image_url:
                    embed.set_image(url=image_url)
                    embed.url = image_url

                offer_end_date = utc.localize(datetime.strptime(
                    game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["endDate"],
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                ))
                embed.set_footer(text=f'Was {game["price"]["totalPrice"]["fmtPrice"]["originalPrice"]} USD, offer ends '
                                      f'{offer_end_date.astimezone(timezone("US/Eastern")).strftime("%Y-%m-%d %I:%M%p")}')

                await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(EpicAlerts(bot))
