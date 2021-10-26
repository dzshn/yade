import asyncio
import contextlib
import io
import pprint
import textwrap
import time
import traceback

from discord.ext import commands

from yade.modules.base import Module
from yade.response import Response
from yade.util import clean_codeblock


class Dev(Module):
    def __init__(self, *_, **__):
        self._last_eval_value = None
        super().__init__(*_, **__)

    @commands.command(name='eval', aliases=['.'])
    async def eval_(self, ctx: commands.Context, *, code: str):
        """Evaluate some code"""
        code = clean_codeblock(code)
        if '\n' not in code:
            code = 'return ' + code
        code = 'async def func():\n' + textwrap.indent(code, '  ')

        code_return = None
        code_stdout = io.StringIO()
        code_stderr = io.StringIO()

        env = {
            '_': self._last_eval_value,
            'b': self.bot,
            'ctx': ctx,
            'author': ctx.author,
            'msg': ctx.message,
        }

        try:
            exec_time = time.perf_counter()
            exec(code, env)
            with contextlib.redirect_stdout(code_stdout), contextlib.redirect_stderr(
                code_stderr
            ):
                code_return = await env['func']()

        except Exception:
            response = Response(
                title='Evaluated code with error!',
                description=f"{(time.perf_counter()-exec_time)*1000:g}ms :clock2:",
                error=True,
                traceback=traceback.format_exc(-1),
                return_=None,
                stdout=code_stdout.getvalue(),
                stderr=code_stderr.getvalue(),
            )

        else:
            response = Response(
                title='Evaluated code with success!',
                description=f"{(time.perf_counter()-exec_time)*1000:g}ms :clock2:",
                return_=pprint.pformat(code_return, compact=True, width=51),
                stdout=code_stdout.getvalue(),
                stderr=code_stderr.getvalue(),
            )

            if code_return is not None:
                self._last_eval_value = code_return

        await ctx.send(embed=response.embed, files=response.files)

    @commands.command(aliases=['h'])
    async def shell(self, ctx: commands.Context, *, command: str):
        command = clean_codeblock(command)
        exec_time = time.perf_counter()
        proc = await asyncio.subprocess.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        try:
            await asyncio.wait_for(proc.wait(), timeout=10)
        except asyncio.TimeoutError:
            proc.kill()

        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            response = Response(
                title='Subprocess finished',
                description=f'{(time.perf_counter()-exec_time)*1000:g}ms :clock2:',
                stdout=stdout.decode(),
                stderr=stderr.decode(),
            )

        else:
            response = Response(
                title=f'Subprocess finished with return {proc.returncode}',
                error=True,
                description=f'{(time.perf_counter()-exec_time)*1000:g}ms :clock2:',
                stdout=stdout.decode(),
                stderr=stderr.decode(),
            )

        await ctx.send(embed=response.embed, files=response.files)

    @commands.group(aliases=['ext', 'exts'])
    async def extensions(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.invoke(self.extensions_list)

    @extensions.command(name='list')
    async def extensions_list(self, ctx: commands.Context):
        exts = self.bot.extensions
        cogs = self.bot.cogs
        await ctx.send(
            f'Loaded extensions ({len(exts)}): '
            + ', '.join(f'`{i}`' for i in exts)
            + '\n'
            + f'Loaded cogs ({len(cogs)}): '
            + ', '.join(f'`{v.__module__}.{k}`' for k, v in cogs.items())
        )

    @extensions.command(name='reload', aliases=['rl', 'l'])
    async def extensions_reload(self, ctx: commands.Context, *exts: str):
        status = []
        for ext in exts:
            try:
                if ext in self.bot.extensions:
                    status.append(f'+++ Reloading {ext}')
                    self.bot.reload_extension(ext)
                else:
                    status.append(f'+++ Loading   {ext}')
                    self.bot.load_extension(ext)

            except (ModuleNotFoundError, commands.ExtensionNotFound):
                status.append('-   Not found!')

            except commands.NoEntryPointError:
                # TODO: Walk submodules if it's a module maybe
                status.append('-   No entry point!')

            except commands.ExtensionError:
                status.append('-   Error!\n' + traceback.format_exc())

            else:
                status.append(f'+   Reloaded  {ext}!')

        response = Response(title='Done!', format_name='diff', output='\n'.join(status))

        await ctx.send(embed=response.embed, files=response.files)
