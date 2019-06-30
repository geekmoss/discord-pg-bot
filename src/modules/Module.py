import discord
from modules import ModulesManager


class Module:
    description = "Abstract module for others."

    COLOR_INFO = discord.Colour.from_rgb(100, 200, 100)
    COLOR_HELP = discord.Colour.from_rgb(0, 255, 0)
    COLOR_ERROR = discord.Colour.from_rgb(255, 0, 0)

    @staticmethod
    def process(msg: discord.Message, prefix=None, mm: ModulesManager = None):
        pass

    @staticmethod
    async def error(msg: discord.Message, content, title="Something is wrong"):
        await msg.channel.send(embed=discord.Embed(
            title=title,
            color=Module.COLOR_ERROR,
            description=content,
        ))
        pass
    pass
