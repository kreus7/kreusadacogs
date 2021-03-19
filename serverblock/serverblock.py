import asyncio
import discord

from redbot.core import commands, Config
from redbot.core.utils.chat_formatting import box
from redbot.core.utils.predicates import MessagePredicate

class ServerBlock(commands.Cog):
    """
    Blocklist guilds from being able to add [botname].
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 34237423098423094, force_registration=True)
        self.config.register_global(blacklist=[])

    @commands.group(aliases=["serverblacklist", "serverblocklist"])
    async def sbl(self, ctx):
        """
        Guild blocklist management.
        """

    @sbl.command(usage="<guild_id>")
    async def add(self, ctx, guild: int):
        """Add a guild to the guild blocklist."""
        b = await self.config.blacklist()
        if guild in b:
            return await ctx.send("This guild is already blocklisted.")
        b.append(guild)
        await self.config.blacklist.set(b)
        msg = "Guild added to blocklist."
        if not guild in [g.id for g in self.bot.guilds]:
            await ctx.send(msg)
        else:
            msg += (
                f" {ctx.me.name} is currently in this guild. Would you like it to leave? (yes/no)"
            )
            await ctx.send(msg)
            get_guild = self.bot.get_guild(guild)
            try:
                pred = MessagePredicate.yes_or_no(ctx, user=ctx.author)
                msg = await ctx.bot.wait_for("message", check=pred, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond, I assumed yes.")
                return await get_guild.leave()

            if pred.result:
                await ctx.send("Done.")
                return await get_guild.leave()
            else:
                await ctx.send(f"Okay, {ctx.me.name} will remain in the guild.")

    @sbl.command(usage="<guild_id>")
    async def remove(self, ctx, guild: int):
        """Remove a guild from the guild blocklist."""
        b = await self.config.blacklist()
        if guild in b:
            b.remove(guild)
            await self.config.blacklist.set(b)
        else:
            return await ctx.send("This guild is not on the blocklist.")
        await ctx.send("Guild removed from blocklist.")

    @sbl.command(name="list")
    async def _list(self, ctx):
        """Lists guilds on the blocklist."""
        b = await self.config.blacklist()
        if not b:
            return await ctx.send("There are no blocklisted guilds.")
        if len(b) == 1:
            s = ''
        else:
            s = 's'
        title = f"Blocklisted guild{s}:"
        await ctx.send(box(title + '\n\n' + "\n".join(f"\t{x}" for x in b), lang='yaml'))

    @sbl.command()
    async def clear(self, ctx):
        """Clears the guild blocklist."""
        await self.config.blacklist.clear()
        await ctx.tick()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        config = await self.config.blacklist()
        if guild.id in config:
            return await guild.leave()