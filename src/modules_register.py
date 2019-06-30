from modules import *


modules = ModulesManager(default_prefix="pg")
modules.add_module('help', Help)
modules.add_module('lobby', Lobbies)
modules.add_module('sm', SteamMatcher)
