import collections
import re
import secrets
import traceback

import discord
from discord.ext import commands

from yade.modules.base import Module
from yade.response import Response

# 'JCatAIO123Thing' -> ['J', 'Cat', 'AIO', '123', 'Thing']
RGX_CAMEL_CASE = re.compile(r'(?:[A-Z]|[0-9]+)(?:[a-z]+|[A-Z]*(?=[A-Z0-9]|$))')
OWNER_BYPASSES = (
    commands.PrivateMessageOnly,
    commands.NoPrivateMessage,
    commands.MissingPermissions,
    commands.MissingRole,
    commands.MissingAnyRole,
    commands.DisabledCommand,
    commands.CommandOnCooldown,
)


def parse_error(error: Exception) -> str:
    return '{}: {}'.format(
        ' '.join(
            w if i == 0 or w.isupper() else w.lower()
            for i, w in enumerate(RGX_CAMEL_CASE.findall(type(error).__name__))
        ),
        error,
    )


ErrorData = collections.namedtuple('ErrorData', 'ctx error')


class ErrorHandler(Module):
    def __init__(self, *args, **kwargs):
        self.__errors: dict[bytes, ErrorData] = {}
        super().__init__(*args, **kwargs)

    @commands.command()
    async def geterror(self, ctx: commands.Context, token: str):
        token = bytes.fromhex(token)
        if token not in self.__errors:
            await ctx.send('No such token')
            return

        index = list(self.__errors.keys()).index(token)
        ctx, error = self.__errors[token]
        response = Response(
            title=f'Data for error #{index}',
            color=0xFA5070,
            traceback=''.join(traceback.format_exception_only(type(error), error)),
            context=(
                f'content: {ctx.message.content}\n'
                f'prefix: {ctx.prefix}\n'
                f'args: {", ".join(repr(i) for i in ctx.args)}\n'
                f'kwargs: {",".join(f"{k}={v!r}" for k, v in ctx.kwargs.items())}\n'
                f'cog: {ctx.cog}\n'
                f'command: {ctx.command}\n'
                f'valid: {ctx.valid}\n'
                f'failed: {ctx.command_failed}\n'
                f'invoked with: {ctx.invoked_with}\n'
                f'invoked parents: {ctx.invoked_parents}\n'
                f'invoked subcommand: {ctx.invoked_subcommand}\n'
                f'subcommand passed: {ctx.subcommand_passed}\n'
                f'in guild: {ctx.guild is not None}\n'
                f'channel perms: {ctx.channel.permissions_for(ctx.me) if ctx.guild else "N/A"}'
            ),
        )

        await ctx.send(embed=response.embed, files=response.files)

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if ctx.command and ctx.command.has_error_handler():
            return

        if ctx.cog and ctx.cog.has_error_handler():
            return

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.CommandInvokeError):
            original: Exception = error.original
            if isinstance(original, discord.Forbidden):
                return

            # This is very likely to break with 1.3 trillion errors.
            token = secrets.token_bytes(10)
            self.__errors[token] = ErrorData(ctx=ctx, error=error)

            if self.bot.owner_ids:
                owner_mentions = ', '.join(f'<@{i}>' for i in self.bot.owner_ids)
            else:
                owner_mentions = f'<@{self.bot.owner_id}>'

            await ctx.send(
                embed=discord.Embed(
                    color=0xFA5050,
                    title='Uncaught error!!',
                    description=(
                        'An uncaught error just occurred:\n'
                        f'\u200b \u200b {parse_error(original)}\n'
                        f'This error has been stored, you can report it to {owner_mentions} '
                        'with below token'
                    ),
                ).set_footer(text=f'Token: {token.hex()}')
            )

        elif isinstance(error, OWNER_BYPASSES) and await self.bot.is_owner(ctx.author):
            if hasattr(ctx, '_bypassed'):
                return
            await ctx.send(f'(bypassed `{error!r}`)')
            ctx._bypassed = True  # Only used to not end in an infinite loop here
            try:
                await ctx.reinvoke(call_hooks=True)
            except Exception as e:
                await self.on_command_error(ctx, e)

        elif isinstance(error, (commands.UserInputError, commands.CheckFailure)):
            await ctx.send(parse_error(error))
