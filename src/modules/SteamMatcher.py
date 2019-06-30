import discord
import shlex
import steam
import config
from steam import WebAPI, SteamID
from modules.Module import Module
from requests import HTTPError


class SteamMatcher(Module):
    description = "Displays the intersection of games from Steam libraries of selected Steam profiles."

    @staticmethod
    async def process(msg: discord.Message, prefix=None, mm=None):
        command = msg.content[len(prefix):].strip()
        if command == "help":
            await SteamMatcher.help(msg, prefix)
            pass
        else:
            try:
                m: discord.Message = await msg.channel.send('Wait a moment...')
                sm = Steam(*shlex.split(command))
                data = sm.compare()

                libs = ', '.join(map(lambda x: f'**{x}** *({data["users"][x]} games)*', data['users']))

                def build_item(game):
                    pt = sum(game["info"]["u"].values())
                    is_mins = pt < 60
                    t = pt if is_mins else pt / 60
                    return f'- **[{game["info"]["name"]}]({game["url"]})**, *playtime of everyone ' \
                        f'`{t:.1f} {"min" if is_mins else "hour"}{"" if t < 2.0 else "s"}`*;'
                    pass

                body = "" + \
                       f"There are {len(data['games'])} matches from {libs} players libraries.\n\n" + \
                       '\n'.join(map(build_item, data['games']))

                if len(body) > 2048:
                    buff = ""
                    msgs = []
                    for l in body.splitlines():
                        if len(buff + l + "\n") <= 2048:
                            buff += l + "\n"
                            pass
                        else:
                            msgs.append(buff)
                            buff = l + "\n"
                            pass
                        pass

                    if buff:
                        msgs.append(buff)

                    await m.delete()
                    for i, n in enumerate(msgs):
                        await msg.channel.send(content=None, embed=discord.Embed(
                            title=f"Steam Matcher Result - Part {i + 1}",
                            color=discord.Colour.from_rgb(66, 244, 125),
                            description=n
                        ))
                    pass
                else:
                    await m.edit(content=None, embed=discord.Embed(
                        title="Steam Matcher Result",
                        color=discord.Colour.from_rgb(66, 244, 125),
                        description=body
                    ))
                    pass
                pass
            except SteamException as e:
                await msg.channel.send(embed=discord.Embed(
                    title="Steam Matcher Errdor",
                    type="rich",
                    color=discord.Colour.from_rgb(216, 34, 34),
                    description=e.args[0] + "\n\n" + f"For usage help: `{prefix} help`"
                ))
            pass
        pass

    @staticmethod
    async def help(msg: discord.Message, prefix):
        await msg.channel.send(
            embed=discord.Embed(title="Steam Matcher Help", type="rich",
                                color=discord.Colour.from_rgb(66, 244, 125),
                                description="Displays the intersection of games from Steam libraries"
                                            " of selected Steam profiles. \n\n" +
                                            f"Usage: `{prefix} SteamID VanityURL UrlOfProfile`\n" +
                                            f"Example: `{prefix} 123456 SomeGamerBoi`\n\n"))
        pass
    pass


class Steam:
    def __init__(self, *users):
        self._api: WebAPI = WebAPI(config.STEAM_KEY)

        if len(users) < 2:
            raise SteamException("At least two users must be entered.")
        self._users = list(map(self.get_user, users))
        pass

    def get_user(self, user: str):
        if user.startswith("https://steamcommunity.com/id/") or user.startswith("https://steamcommunity.com/profiles/"):
            u = user.replace("//", "/", 1).split("/", 3)[-1]
            return steam.steamid.from_url(user), u if u[-1] != "/" else u[:-1]

        res = self._api.call("ISteamUser.ResolveVanityURL", vanityurl=user, url_type=1)
        if res["response"]["success"] == 1:
            return SteamID(res["response"]["steamid"]), user
        else:
            # TODO: Logging
            print(res)
            pass

        if user.isnumeric():
            res = self._api.call("ISteamUser.GetPlayerSummaries", steamids=user)
            if isinstance(res["response"]["players"], list) and len(res["response"]["players"]) == 1:
                u = res["response"]["players"][0]
                return SteamID(u["steamid"]), u["personaname"]
            elif isinstance(res["response"]["players"], dict) and len(res["response"]["players"]["player"]) == 1:
                u = res["response"]["players"]["player"][0]
                return SteamID(u["steamid"]), u["personaname"]
            else:
                print(res)
                pass
            pass
        raise SteamException(f"User {user} not found.")

    def get_library(self, user: SteamID, include_played_free_games=True, include_appinfo=True):
        try:
            return self._api.call("IPlayerService.GetOwnedGames", steamid=user.as_64, include_appinfo=include_appinfo,
                                  include_played_free_games=include_played_free_games, appids_filter=[])["response"]
        except HTTPError:
            return None
        pass

    def compare(self):
        game_url = "https://store.steampowered.com/app/"
        libs = {}
        counts = {}
        apps = {}
        for u in self._users:
            lib = self.get_library(u[0])
            if not lib:
                counts[u[1]] = 0
                libs[u[1]] = []
                continue

            libs[u[1]] = set()
            for g in lib["games"]:
                libs[u[1]].add(g["appid"])

                if g["appid"] in apps:
                    apps[g["appid"]]["u"][u[1]] = g["playtime_forever"]
                    pass
                else:
                    apps[g["appid"]] = {
                        "name": g["name"],
                        "u": {u[1]: g["playtime_forever"]},
                    }
                    pass
                pass

            counts[u[1]] = lib["game_count"]
            pass

        intersection = libs[self._users[0][1]]
        for l in libs:
            intersection &= libs[l]
            pass

        games = list(map(lambda x: {"appid": x, "url": game_url + str(x), "info": apps[x]}, intersection))
        games.sort(key=lambda x: x["info"]["name"])
        return {"users": counts, "games": games}
    pass


class SteamException(Exception):
    pass
