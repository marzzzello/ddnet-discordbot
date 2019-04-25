#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from typing import List, Union

import discord
from discord.ext import commands

YES     = '<:f3:397431188941438976>'
NO      = '<:f4:397431204552376320>'
CANCEL  = '\N{NO ENTRY SIGN}'


class Votes(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.votes = {}


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]) -> None:
        message = reaction.message
        if message.id not in self.votes:
            return

        emoji = str(reaction.emoji)
        if emoji == YES:
            self.votes[message.id] += 1
        elif emoji == NO:
            self.votes[message.id] -= 1
        elif emoji == CANCEL and user.guild_permissions.kick_members:
            if user == self.bot.user:
                return
            del self.votes[message.id]
        else:
            try:
                await message.remove_reaction(emoji, user)
            except discord.Forbidden:
                pass


    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]) -> None:
        message = reaction.message
        if message.id not in self.votes:
            return

        emoji = str(reaction.emoji)
        if emoji == YES:
            self.votes[message.id] -= 1
        elif emoji == NO:
            self.votes[message.id] += 1


    @commands.Cog.listener()
    async def on_reaction_clear(self, message: discord.Message, reactions: List[discord.Reaction]) -> None:
        if message.id not in self.votes:
            return

        self.votes[message.id] = 0


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, *, user: discord.Member) -> None:
        msg = f'{ctx.author.mention} called for vote to kick {user.mention}'
        message = await ctx.send(msg)

        self.votes[message.id] = 0

        try:
            for emoji in (YES, NO, CANCEL):
                await message.add_reaction(emoji.strip('<>'))  # TODO: Remove strip when discord.py 1.1.0 releases
        except discord.Forbidden:
            pass

        i = 30
        while i >= 0:
            if message.id not in self.votes:
                break

            await message.edit(content=f'{msg}. {i}s left')

            i -= 1
            await asyncio.sleep(1)

        result = self.votes.pop(message.id, 0)
        if result > 0:
            result_msg = 'Vote passed'
            try:
                await user.kick(reason='Kicked by vote')
            except discord.Forbidden:
                pass
            else:
                result_msg += f'. {user.mention} kicked by vote'
        else:
            result_msg = 'Vote failed'

        await ctx.send(result_msg)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Votes(bot))