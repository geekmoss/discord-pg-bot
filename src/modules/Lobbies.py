import discord
import shlex
from modules.Module import Module
from db import Lobby, LobbyList


class Lobbies(Module):
    description = "Module for lobbies interact."

    @staticmethod
    async def process(msg: discord.Message, prefix=None, mm=None):
        command = msg.content[len(prefix):].strip()
        parts = shlex.split(command)

        if command == "" or command.lower() == "help":
            await Lobbies.help(msg.channel, prefix)
            return

        if parts[0] == "list":
            await Lobbies.list(msg, prefix, parts[1] if len(parts) > 1 else None)
            return
        elif parts[0] == "join":
            if len(parts) > 1 and str.isnumeric(parts[1]):
                try:
                    await Lobbies.join(msg, int(parts[1]), prefix)
                except ValueError:
                    await Module.error(msg, f"Please type the command correctly.\nExample: `{prefix} join 13`")
                pass
            else:
                await Module.error(msg, f"Please type the command correctly.\nExample: `{prefix} join 13`")
            return
        elif parts[0] == "leave":
            if len(parts) > 1 and str.isnumeric(parts[1]):
                try:
                    await Lobbies.leave(msg, parts[1], prefix)
                except ValueError:
                    await Module.error(msg, f"Please type the command correctly.\nExample: `{prefix} join 13`")
                pass
            else:
                await Module.error(msg, f"Please type the command correctly.\nExample: `{prefix} join 13`")
            return
        elif parts[0] == "create" and len(parts) > 1:
            await Lobbies.create(msg, parts[1], parts[2] if len(parts) > 2 and parts[2].isnumeric() else 0)
            return
        elif parts[0] == "delete":
            await Lobbies.delete(msg, parts[1], prefix)
            return
        elif parts[0] == "mention":
            await Lobbies.mention(msg, parts[1], prefix)
            return

        await msg.channel.send(f"Sorry {msg.author.mention}, I don't know command: `{command}`")
        pass

    @staticmethod
    async def list(msg: discord.Message, p, lid=None):
        chn: discord.TextChannel = msg.channel

        if lid:
            try:
                l: Lobby = Lobby.get_or_none(int(lid))
                if not l:
                    await Module.error(msg, f"Lobby not found, check your command or try use  `{p} list`")
                    return

                users = LobbyList.select().where(LobbyList.lobby == l.id).execute()
                users_list = list(users)

                users_desc = "\n".join(map(lambda x: f"- {x.user}, joined {x.joined:%Y-%m-%d %H:%M}", users_list))

                await msg.channel.send(embed=discord.Embed(
                    title=f"Details of {l.subject}",
                    color=Module.COLOR_INFO,
                    description=f"**Author**: {l.author}\n"
                    f"**Created**: {l.created:%Y-%m-%d %H:%M}\n"
                    f"**Slots**: `{len(users_list)}` / `{l.slots if l.slots > 0 else 'Unlimited'}`\n"
                    f"\n\n"
                    f"Users:\n{users_desc}"
                ))
                pass
            except ValueError:
                await Module.error(msg, f"Please type the command correctly.\nExample: `{p} list 13`")
            return

        lobbies = list(Lobby.select().where(Lobby.server == chn.guild.id).execute())
        if lobbies:
            content = ""
            for lobby in lobbies:
                content += f"**`{lobby.id}`**: {lobby.subject}\n"
                pass

            await msg.channel.send(embed=discord.Embed(
                title="List of lobbies",
                color=discord.Colour.from_rgb(150, 200, 150),
                description=content
            ))
            pass
        else:
            await msg.channel.send(embed=discord.Embed(
                title="List of lobbies",
                color=discord.Colour.from_rgb(50, 50, 200),
                description="There is currently no lobby on this server."
            ))
        pass

    @staticmethod
    async def join(msg: discord.Message, lobby_id, p):
        l: Lobby = Lobby.get_or_none(Lobby.id == int(lobby_id))
        if l:
            p = LobbyList.get_or_none(LobbyList.user == msg.author.display_name)
            if p:
                await msg.channel.send(embed=discord.Embed(
                    title="Info",
                    color=Module.COLOR_INFO,
                    description="You are already joined in lobby."
                ))
                return
            else:
                LobbyList.create(lobby=l.id, user=msg.author.display_name, user_mention=msg.author.mention)
                await msg.channel.send(embed=discord.Embed(
                    title="Info",
                    color=Module.COLOR_INFO,
                    description="Welcome to lobby!"
                ))
                return
            pass
        else:
            await Module.error(msg, f"Lobby not found, check your command or try use  `{p} list`.")
        pass

    @staticmethod
    async def leave(msg: discord.Message, id_lobby, p):
        l: Lobby = Lobby.get_or_none(Lobby.id == int(id_lobby))
        if l:
            ll: LobbyList = LobbyList.get_or_none(
                (LobbyList.lobby == id_lobby) & (LobbyList.user_mention == msg.author.mention)
            )

            if not ll:
                await Module.error(msg, f"You are not joined to the selected lobby.")
                return

            if l.author_mention == msg.author.mention:
                await Module.error(msg, "You are the founder of the lobby, you can't leave it. "
                                        "If you want to leave the lobby, you can remove it."
                                        "Use:"
                                        f"`{p} remove {id_lobby}`")
                pass
            else:
                ll.delete_instance()
                await Module.error(msg, "You left the lobby.")
                pass
            pass
        else:
            await Module.error(msg, f"Lobby not found, check your command or try use  `{p} list`.")
            pass
        pass

    @staticmethod
    async def create(msg: discord.Message, name, slots=0):
        if slots == 1:
            slots = 2
            pass

        l: Lobby = Lobby.create(subject=name, author=msg.author.display_name, author_mention=msg.author.mention,
                                slots=slots, server=msg.guild.id)

        LobbyList.create(lobby=l.id, user=msg.author.display_name, user_mention=msg.author.mention)

        await msg.channel.send(f"Hey {msg.author.mention}, your lobby *{name}* has been created with ID `{l.id}`.")
        pass

    @staticmethod
    async def delete(msg: discord.Message, id_lobby, p):
        l: Lobby = Lobby.get_or_none(Lobby.id == int(id_lobby))
        if l:
            if l.author_mention == msg.author.mention:
                l.delete_instance(recursive=True)
                await Module.error(msg, "You removed the lobby.")
                pass
            else:
                await Module.error(msg, "You are not the founder of the lobby. ")
                pass
            pass
        else:
            await Module.error(msg, f"Lobby not found, check your command or try use  `{p} list`.")
            pass
        pass

    @staticmethod
    async def mention(msg: discord.Message, id_lobby, p):
        l: Lobby = Lobby.get_or_none(Lobby.id == int(id_lobby))
        if not l:
            await Module.error(msg, f"Lobby not found, check your command or try use  `{p} list`.")
            return

        if l.author_mention != msg.author.mention:
            await Module.error(msg, f"You are not a founder of this lobby.")
            return

        content_msg = "Hey, wake up!\n"
        mentions = []
        for row in LobbyList.select().where(LobbyList.lobby == int(id_lobby)):
            mentions.append(row.user_mention)
            pass

        content = content_msg + " • ".join(mentions)
        if len(content) > 2000:
            content = content_msg
            for item in mentions:
                if content == "":
                    content = item
                    continue

                if len(content + " • " + item) < 2000:
                    content += " • " + item
                else:
                    await msg.channel.send(content)
                    content = ""
                    pass
                pass
        else:
            await msg.channel.send(content)
            pass
        pass

    @staticmethod
    async def help(channel: discord.TextChannel, p):
        await channel.send(embed=discord.Embed(
            title="Help of lobby module",
            color=Module.COLOR_HELP,
            description=f"Lobby module commands:\n"
            f"- `{p} list` for list of lobbies\n"
            f"- `{p} list ID` for info about lobby with `ID`\n"
            f"- `{p} join ID` for join into lobby with `ID`\n"
            f"- `{p} leave ID` for leave selected lobby\n"
            f"- `{p} create NAME [SLOTS]` for create lobby with `NAME`, and optional can be set "
            "maximum users (`SLOTS`)\n"
            "For lobby owner:\n"
            f"- `{p} lobby remove ID` for remove selected lobby\n"
            f"- `{p} lobby mention ID` for mention all of joined users\n"
            "\n\n"
            f"Example:\n"
            "```\n"
            f"{p} create \"Operation Overlord (ARMA)\"\n"
            f"{p} create \"DotA 4 fun\" 5\n"
            "```"
        ))
        pass

    pass
