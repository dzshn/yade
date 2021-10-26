import io
from typing import Optional

import discord

from yade.util import codeblock


class Response:
    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        error: bool = False,
        format_name: str = 'py',
        color: Optional[int] = None,
        **kwargs: str,
    ):
        self._title = title
        self._desc = description
        self._error = error
        self._fmt = format_name
        self._color = color
        self._kwg = {k: v for k, v in kwargs.items() if v}

    @property
    def embed(self) -> discord.Embed:
        if self._error:
            embed = discord.Embed(
                color=self._color or 0xFA5050, title=f':x: {self._title}'
            )
        else:
            embed = discord.Embed(
                color=self._color or 0x50FA50, title=f':white_check_mark: {self._title}'
            )

        if self._desc:
            embed.description = self._desc

        for name, value in self._kwg.items():
            if value:
                embed.add_field(
                    name=name.replace('_', ' ').strip().title(),
                    value=codeblock(value, format_name=self._fmt),
                    inline=False,
                )

        return embed

    @property
    def files(self) -> list[discord.File]:
        return [
            discord.File(io.StringIO(value), filename=f'full_{name}.{self._fmt}')
            for name, value in self._kwg.items()
            if len(value) >= 1000
        ]
