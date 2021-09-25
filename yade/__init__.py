from discord.ext import commands

from yade.modules.dev import Dev

MODULES = [Dev]


class Yade(*MODULES):
    pass


def setup(bot: commands.Bot):
    """Entry point for dpy"""
    bot.add_cog(Yade(bot))
