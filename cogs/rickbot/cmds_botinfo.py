"""
(c) 2024 Zachariah Michael Lagden (All Rights Reserved)
You may not use, copy, distribute, modify, or sell this code without the express permission of the author.

This cog counts the number of times a user has said the n-word in the server and provides a command to check the records,
as well as a leaderboard command that shows the top 10 users with the most n-word records.
"""

# Python standard library
from datetime import datetime

# Third-party libraries
from discord_timestamps import format_timestamp, TimestampType
from discord.ext import commands
import discord
import requests

# Helper functions
from helpers.colors import MAIN_EMBED_COLOR, ERROR_EMBED_COLOR

# Config
from config import CONFIG


class RickBot_BotInfoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.GITHUB_API = (
            CONFIG["repo"]["url"]
            if "repo" in CONFIG
            and "url" in CONFIG["repo"]
            and CONFIG["repo"]["url"] != ""
            else None
        )

    def botownercheck(ctx):
        return ctx.author.id in CONFIG["devs"]

    @commands.command(name="updates")
    async def _updates(self, ctx):
        """
        Check github for the latest commits, provides the last 5 along with other relevant information.
        """

        if self.GITHUB_API is None:
            embed = discord.Embed(
                title="Sorry!",
                description="This command is disabled.",
                color=ERROR_EMBED_COLOR,
            )

            await ctx.message.reply(embed=embed, mention_author=False)
            return

        query = requests.get(self.GITHUB_API)

        if query.status_code != 200:
            embed = discord.Embed(
                title="Error",
                description="I'm sorry, there was an error fetching the latest commits. Please try again later.\nIf the problem persists, please contact the bot owner.",
                color=ERROR_EMBED_COLOR,
            )

            await ctx.message.reply(embed=embed, mention_author=False)
            return

        data = query.json()

        if not isinstance(data, list):
            embed = discord.Embed(
                title="Error",
                description="I'm sorry, there was an error fetching the latest commits. Please try again later.\nIf the problem persists, please contact the bot owner.",
                color=ERROR_EMBED_COLOR,
            )

            await ctx.message.reply(embed=embed, mention_author=False)
            return

        # Sort the commits by date (newest first)
        sorted_commits = sorted(
            data,
            key=lambda x: datetime.strptime(
                x["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ"
            ),
            reverse=True,
        )

        # Extract required information
        commit_list = []
        for commit in sorted_commits:
            commit_info = {
                "sha": commit["sha"],
                "id": commit["sha"][0:7],
                "date": commit["commit"]["author"]["date"],
                "author": commit["commit"]["author"]["name"],
                "author_html_url": commit["author"]["html_url"],
                "email": commit["commit"]["author"]["email"],
                "short_message": commit["commit"]["message"].split("\n")[0],
                "full_message": commit["commit"]["message"],
                "url": commit["url"],
                "html_url": commit["html_url"],
            }
            commit_list.append(commit_info)

        # Create the embed

        desc = "Here are the latest updates to the bot:\n\n"

        for commit in commit_list[:5]:
            date = datetime.strptime(commit["date"], "%Y-%m-%dT%H:%M:%SZ")

            desc += f"**[`{commit['id']}`]({commit['html_url']})** - {format_timestamp(date, TimestampType.RELATIVE)} by [{commit['author'].split(' ')[0]}]({commit['author_html_url']})\n{commit['short_message']}\n\n"

        embed = discord.Embed(
            title="Latest Updates",
            description=desc,
            color=MAIN_EMBED_COLOR,
        )

        embed.set_footer(
            text="Better Hood Bot is a project by Zach. All rights reserved."
        )

        await ctx.message.reply(embed=embed, mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(RickBot_BotInfoCommands(bot))
