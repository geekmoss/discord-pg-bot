from modules_register import modules
import config
import discord
import click
from db import check_db

client = discord.Client()


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.change_presence(
        activity=discord.Activity(name=f"Use: {modules.prefix} help", type=discord.ActivityType.listening)
    )
    pass


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    await modules.call(message)
    return


@click.command()
@click.option('--discord-token', default=config.DISCORD_TOKEN)
def cli(discord_token):
    config.DISCORD_TOKEN = discord_token
    client.run(config.DISCORD_TOKEN)
    pass


if __name__ == "__main__":
    check_db()
    cli()
    pass
