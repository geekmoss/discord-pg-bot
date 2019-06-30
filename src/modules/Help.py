import discord
from modules.Module import Module


class Help(Module):
    description = "This help."

    @staticmethod
    async def process(msg: discord.Message, prefix=None, mm=None):
        content = "Available modules: \n"
        for key in mm.modules:
            content += f" - `{key}` {mm.modules[key].description}\n"

        await msg.channel.send(content=None, embed=discord.Embed(
            title="LobbyBot Help",
            color=discord.Colour.from_rgb(66, 244, 125),
            description=content
        ))
        pass
    pass
