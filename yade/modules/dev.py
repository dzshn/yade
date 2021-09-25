from discord.ext import commands

from yade.modules.base import Module


class Dev(Module):
    @commands.command(aliases=['.'])
    async def eval(self, ctx: commands.Context, *, code: str):
        ...

    @commands.command()
    async def inspect(self, ctx: commands.Context, *, object: str):
        ...

    @commands.command()
    async def shell(self, ctx: commands.Context, *, command: str):
        ...
