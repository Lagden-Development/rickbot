"""
RickBot 2.0 - Autocomplete Examples Cog

Demonstrates various autocomplete patterns for slash command parameters.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import TYPE_CHECKING, List

from helpers.colors import MAIN_EMBED_COLOR, SUCCESS_EMBED_COLOR

if TYPE_CHECKING:
    from core.bot import RickBot


# Sample data for autocomplete examples
PROGRAMMING_LANGUAGES = [
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "C++",
    "C#",
    "Go",
    "Rust",
    "Ruby",
    "PHP",
    "Swift",
    "Kotlin",
    "Dart",
    "Scala",
    "Haskell",
    "Elixir",
    "Clojure",
    "Lua",
    "Perl",
    "R",
    "MATLAB",
    "Julia",
    "F#",
    "OCaml",
]

GAME_DATABASE = {
    "Minecraft": {"genre": "Sandbox", "release": "2011"},
    "Terraria": {"genre": "Sandbox", "release": "2011"},
    "Stardew Valley": {"genre": "Simulation", "release": "2016"},
    "Hollow Knight": {"genre": "Metroidvania", "release": "2017"},
    "Celeste": {"genre": "Platformer", "release": "2018"},
    "Hades": {"genre": "Roguelike", "release": "2020"},
    "Among Us": {"genre": "Social Deduction", "release": "2018"},
    "Valorant": {"genre": "FPS", "release": "2020"},
    "League of Legends": {"genre": "MOBA", "release": "2009"},
    "Dota 2": {"genre": "MOBA", "release": "2013"},
    "Counter-Strike 2": {"genre": "FPS", "release": "2023"},
    "Overwatch 2": {"genre": "FPS", "release": "2022"},
    "Apex Legends": {"genre": "Battle Royale", "release": "2019"},
    "Fortnite": {"genre": "Battle Royale", "release": "2017"},
    "Elden Ring": {"genre": "RPG", "release": "2022"},
    "The Witcher 3": {"genre": "RPG", "release": "2015"},
    "Cyberpunk 2077": {"genre": "RPG", "release": "2020"},
    "Red Dead Redemption 2": {"genre": "Action-Adventure", "release": "2018"},
    "Grand Theft Auto V": {"genre": "Action-Adventure", "release": "2013"},
    "Portal 2": {"genre": "Puzzle", "release": "2011"},
}

POKEMON_BY_TYPE = {
    "Fire": ["Charizard", "Blaziken", "Infernape", "Arcanine", "Typhlosion"],
    "Water": ["Blastoise", "Gyarados", "Greninja", "Swampert", "Milotic"],
    "Grass": ["Venusaur", "Sceptile", "Torterra", "Decidueye", "Rillaboom"],
    "Electric": ["Pikachu", "Raichu", "Luxray", "Magnezone", "Zeraora"],
    "Psychic": ["Mewtwo", "Alakazam", "Espeon", "Gardevoir", "Metagross"],
    "Dragon": ["Dragonite", "Salamence", "Garchomp", "Hydreigon", "Dragapult"],
    "Dark": ["Umbreon", "Tyranitar", "Absol", "Zoroark", "Grimmsnarl"],
    "Fairy": ["Sylveon", "Gardevoir", "Togekiss", "Mimikyu", "Alcremie"],
}


class AutocompleteExamples(commands.Cog):
    """Autocomplete examples for slash command parameters"""

    def __init__(self, bot: "RickBot"):
        self.bot = bot

    # ===========================
    # Basic Static Autocomplete
    # ===========================

    @app_commands.command(
        name="autocomplete_basic", description="Basic autocomplete with static choices"
    )
    @app_commands.describe(language="Choose a programming language")
    async def autocomplete_basic(self, interaction: discord.Interaction, language: str):
        """Basic autocomplete example with static list"""
        embed = discord.Embed(
            title="✅ Language Selected",
            description=f"You chose: **{language}**",
            color=SUCCESS_EMBED_COLOR,
        )
        embed.add_field(
            name="How it works",
            value=(
                "This uses a simple autocomplete function that:\n"
                "1. Filters a static list of languages\n"
                "2. Matches user input (case-insensitive)\n"
                "3. Returns up to 25 results"
            ),
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    @autocomplete_basic.autocomplete("language")
    async def language_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        """Simple autocomplete for programming languages"""
        return [
            app_commands.Choice(name=lang, value=lang)
            for lang in PROGRAMMING_LANGUAGES
            if current.lower() in lang.lower()
        ][:25]

    # ===========================
    # Fuzzy Matching Autocomplete
    # ===========================

    @app_commands.command(
        name="autocomplete_fuzzy",
        description="Fuzzy matching autocomplete (matches anywhere in string)",
    )
    @app_commands.describe(game="Search for a game")
    async def autocomplete_fuzzy(self, interaction: discord.Interaction, game: str):
        """Fuzzy matching autocomplete example"""
        game_info = GAME_DATABASE.get(game, {"genre": "Unknown", "release": "Unknown"})

        embed = discord.Embed(title=f"🎮 {game}", color=SUCCESS_EMBED_COLOR)
        embed.add_field(name="Genre", value=game_info["genre"], inline=True)
        embed.add_field(name="Release", value=game_info["release"], inline=True)
        embed.add_field(
            name="How it works",
            value=(
                "This autocomplete:\n"
                "1. Matches partial strings anywhere in the game name\n"
                "2. Case-insensitive matching\n"
                "3. Shows genre and release year in choices"
            ),
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    @autocomplete_fuzzy.autocomplete("game")
    async def game_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        """Fuzzy matching autocomplete with additional info"""
        current_lower = current.lower()

        choices = []
        for game_name, game_info in GAME_DATABASE.items():
            if current_lower in game_name.lower():
                # Show additional info in choice name
                choice_display = f"{game_name} ({game_info['genre']})"
                choices.append(
                    app_commands.Choice(name=choice_display, value=game_name)
                )

        return choices[:25]

    # ===========================
    # Context-Aware Autocomplete
    # ===========================

    @app_commands.command(
        name="autocomplete_context",
        description="Autocomplete that depends on another parameter",
    )
    @app_commands.describe(
        pokemon_type="Choose a Pokémon type", pokemon="Choose a Pokémon of that type"
    )
    async def autocomplete_context(
        self, interaction: discord.Interaction, pokemon_type: str, pokemon: str
    ):
        """Context-aware autocomplete example"""
        embed = discord.Embed(
            title=f"✅ {pokemon}",
            description=f"Type: **{pokemon_type}**",
            color=SUCCESS_EMBED_COLOR,
        )
        embed.add_field(
            name="How it works",
            value=(
                "The Pokémon autocomplete:\n"
                "1. Checks what type you selected\n"
                "2. Only shows Pokémon of that type\n"
                "3. Adapts dynamically based on context"
            ),
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    @autocomplete_context.autocomplete("pokemon_type")
    async def type_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete for Pokémon types"""
        return [
            app_commands.Choice(name=ptype, value=ptype)
            for ptype in POKEMON_BY_TYPE.keys()
            if current.lower() in ptype.lower()
        ][:25]

    @autocomplete_context.autocomplete("pokemon")
    async def pokemon_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        """Context-aware autocomplete that depends on selected type"""
        # Get the current value of pokemon_type parameter
        # Access through interaction namespace
        namespace = interaction.namespace
        selected_type = getattr(namespace, "pokemon_type", None)

        # If no type selected yet, show all Pokémon
        if not selected_type or selected_type not in POKEMON_BY_TYPE:
            all_pokemon = [
                p for pokemon_list in POKEMON_BY_TYPE.values() for p in pokemon_list
            ]
            return [
                app_commands.Choice(name=pokemon, value=pokemon)
                for pokemon in all_pokemon
                if current.lower() in pokemon.lower()
            ][:25]

        # Filter by selected type
        pokemon_list = POKEMON_BY_TYPE.get(selected_type, [])
        return [
            app_commands.Choice(name=pokemon, value=pokemon)
            for pokemon in pokemon_list
            if current.lower() in pokemon.lower()
        ][:25]

    # ===========================
    # Database-Backed Autocomplete
    # ===========================

    @app_commands.command(
        name="autocomplete_database", description="Autocomplete from database queries"
    )
    @app_commands.describe(command="Search for a command in the database")
    async def autocomplete_database(
        self, interaction: discord.Interaction, command: str
    ):
        """Database-backed autocomplete example"""
        # Get command stats from database
        stats = await self.bot.db.command_logs.find_many(
            filter={"command_name": command}, limit=1
        )

        embed = discord.Embed(title=f"📊 /{command}", color=SUCCESS_EMBED_COLOR)

        if stats:
            total_uses = await self.bot.db.command_logs.count({"command_name": command})
            embed.add_field(name="Total Uses", value=f"{total_uses:,}", inline=True)
            embed.add_field(
                name="Last Used",
                value=stats[0].executed_at.strftime("%Y-%m-%d"),
                inline=True,
            )
        else:
            embed.description = "No usage data available for this command."

        embed.add_field(
            name="How it works",
            value=(
                "This autocomplete:\n"
                "1. Queries the database for command logs\n"
                "2. Aggregates unique command names\n"
                "3. Shows results with usage counts\n"
                "4. Updates in real-time as commands are used"
            ),
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    @autocomplete_database.autocomplete("command")
    async def command_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        """Database-backed autocomplete for command names"""
        try:
            # Aggregate unique command names from database
            pipeline = [
                {"$group": {"_id": "$command_name", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 100},  # Get top 100 commands
            ]

            results = await self.bot.db.command_logs.aggregate(pipeline)

            # Filter by current input
            choices = []
            for result in results:
                command_name = result["_id"]
                if current.lower() in command_name.lower():
                    # Show usage count in choice
                    count = result["count"]
                    choice_display = f"/{command_name} ({count:,} uses)"
                    choices.append(
                        app_commands.Choice(name=choice_display, value=command_name)
                    )

            return choices[:25]

        except Exception:
            # Fallback to empty list if database query fails
            return []

    # ===========================
    # User/Member Autocomplete
    # ===========================

    @app_commands.command(
        name="autocomplete_users",
        description="Autocomplete for server members (by username)",
    )
    @app_commands.describe(username="Search for a member by username")
    @app_commands.guild_only()
    async def autocomplete_users(self, interaction: discord.Interaction, username: str):
        """User search autocomplete example"""
        # Find member by username
        member = discord.utils.find(
            lambda m: m.name.lower() == username.lower()
            or m.display_name.lower() == username.lower(),
            interaction.guild.members,
        )

        if not member:
            await interaction.response.send_message(
                f"❌ Member '{username}' not found!", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"👤 {member.display_name}",
            description=f"@{member.name}",
            color=SUCCESS_EMBED_COLOR,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=str(member.id), inline=True)
        embed.add_field(
            name="Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=True
        )
        embed.add_field(name="Roles", value=f"{len(member.roles) - 1}", inline=True)

        embed.add_field(
            name="How it works",
            value=(
                "This autocomplete:\n"
                "1. Searches guild members by username\n"
                "2. Shows both username and display name\n"
                "3. Limits results to prevent rate limits"
            ),
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    @autocomplete_users.autocomplete("username")
    async def username_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete for guild members"""
        if not interaction.guild:
            return []

        current_lower = current.lower()
        choices = []

        for member in interaction.guild.members:
            # Skip bots
            if member.bot:
                continue

            # Check username or display name
            if (
                current_lower in member.name.lower()
                or current_lower in member.display_name.lower()
            ):
                # Show both username and display name if different
                if member.name != member.display_name:
                    choice_display = f"{member.display_name} (@{member.name})"
                else:
                    choice_display = member.name

                choices.append(
                    app_commands.Choice(name=choice_display[:100], value=member.name)
                )

                # Limit to 25 results
                if len(choices) >= 25:
                    break

        return choices

    # ===========================
    # Dynamic API Simulation
    # ===========================

    @app_commands.command(
        name="autocomplete_dynamic",
        description="Simulates autocomplete with external API data",
    )
    @app_commands.describe(query="Search query")
    async def autocomplete_dynamic(self, interaction: discord.Interaction, query: str):
        """Dynamic autocomplete simulation"""
        embed = discord.Embed(
            title=f"🔍 Search Results: {query}",
            description="This would fetch real data from an API!",
            color=SUCCESS_EMBED_COLOR,
        )
        embed.add_field(
            name="How it works",
            value=(
                "In production, this would:\n"
                "1. Call an external API (GitHub, Spotify, etc.)\n"
                "2. Cache results to avoid rate limits\n"
                "3. Update dynamically as user types\n"
                "4. Handle API errors gracefully"
            ),
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    @autocomplete_dynamic.autocomplete("query")
    async def query_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        """Simulated API autocomplete"""
        # In production, you would:
        # 1. Make async HTTP request to API
        # 2. Parse JSON response
        # 3. Return formatted choices
        # 4. Implement caching/rate limiting

        # Simulation of API results
        if len(current) < 2:
            return [
                app_commands.Choice(name="Type at least 2 characters...", value=current)
            ]

        simulated_results = [
            f"{current} - Result 1",
            f"{current} - Result 2",
            f"{current} - Result 3",
            f"Popular: {current}",
            f"Trending: {current}",
        ]

        return [
            app_commands.Choice(name=result, value=result)
            for result in simulated_results
        ][:25]

    # ===========================
    # Info Command
    # ===========================

    @app_commands.command(
        name="autocomplete_info", description="Learn about autocomplete implementation"
    )
    async def autocomplete_info(self, interaction: discord.Interaction):
        """Information about autocomplete implementation"""
        embed = discord.Embed(
            title="📚 Autocomplete Guide",
            description="Learn how to implement autocomplete in discord.py!",
            color=MAIN_EMBED_COLOR,
        )

        embed.add_field(
            name="Basic Usage",
            value=(
                "```python\n"
                "@app_commands.command()\n"
                "async def my_command(\n"
                "    self,\n"
                "    interaction: discord.Interaction,\n"
                "    item: str\n"
                "):\n"
                "    ...\n\n"
                "@my_command.autocomplete('item')\n"
                "async def item_autocomplete(\n"
                "    self,\n"
                "    interaction: discord.Interaction,\n"
                "    current: str\n"
                ") -> List[app_commands.Choice[str]]:\n"
                "    return [Choice(name=i, value=i) for i in items]\n"
                "```"
            ),
            inline=False,
        )

        embed.add_field(
            name="Best Practices",
            value=(
                "• Always return max 25 choices\n"
                "• Filter based on `current` parameter\n"
                "• Use case-insensitive matching\n"
                "• Handle errors gracefully\n"
                "• Cache API results when possible\n"
                "• Keep autocomplete functions fast (<3s)"
            ),
            inline=False,
        )

        embed.add_field(
            name="Available Examples",
            value=(
                "• `/autocomplete_basic` - Static list\n"
                "• `/autocomplete_fuzzy` - Fuzzy matching\n"
                "• `/autocomplete_context` - Context-aware\n"
                "• `/autocomplete_database` - Database-backed\n"
                "• `/autocomplete_users` - Member search\n"
                "• `/autocomplete_dynamic` - API simulation"
            ),
            inline=False,
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: "RickBot"):
    """Load the AutocompleteExamples cog"""
    await bot.add_cog(AutocompleteExamples(bot))
