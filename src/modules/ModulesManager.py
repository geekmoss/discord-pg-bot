import discord


class ModulesManager:
    def __init__(self, default_prefix):
        self.prefix = default_prefix
        self.modules = {}
        pass

    def add_module(self, command, module, prefix=None):
        prefix = prefix if prefix else self.prefix
        prefix_command = f"{prefix}{' ' if prefix[-1] != ' ' else ''}{command}"
        self.modules[prefix_command] = module

    async def call(self, msg: discord.Message):
        for key in self.modules:
            if msg.content.lower().startswith(key):
                await self.modules[key].process(msg, prefix=key, mm=self)
                pass
            pass
        pass
    pass
