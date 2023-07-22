import discord
from discord.ext.commands import Context

from helpers.mr_engineer_bot import MrEngineer


async def handle_command_on_cooldown(context: Context, error) -> None:
    minutes, seconds = divmod(error.retry_after, 60)
    hours, minutes = divmod(minutes, 60)
    hours = hours % 24
    embed = discord.Embed(
        description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
        color=0xE02B2B,
    )
    await context.send(embed=embed)


async def handle_user_blacklisted(context: Context, bot: MrEngineer) -> None:
    embed = discord.Embed(
        description="You are blacklisted from using the bot!", color=0xE02B2B
    )
    await context.send(embed=embed)
    if context.guild:
        bot.logger.warning(
            "%s (ID: %s) tried to execute a command in the guild %s (ID: %s), but the user is blacklisted from using the bot.",
            context.author,
            context.author.id,
            context.guild.name,
            context.guild.id,
        )
    else:
        bot.logger.warning(
            "%s (ID: %s) tried to execute a command in the bot's DMs, but the user is blacklisted from using the bot.",
            context.author,
            context.author.id,
        )


async def handle_user_not_owner(context: Context, bot: MrEngineer) -> None:
    embed = discord.Embed(
        description="You are not the owner of the bot!", color=0xE02B2B
    )
    await context.send(embed=embed)
    if context.guild:
        bot.logger.warning(
            "%s (ID: %s) tried to execute an owner only command in the guild %s (ID: %s), but the user is not an owner of the bot.",
            context.author,
            context.author.id,
            context.guild.name,
            context.guild.id,
        )
    else:
        bot.logger.warning(
            "%s (ID: %s) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot.",
            context.author,
            context.author.id,
        )


async def handle_missing_permissions(context: Context, error) -> None:
    embed = discord.Embed(
        description="You are missing the permission(s) `"
        + ", ".join(error.missing_permissions)
        + "` to execute this command!",
        color=0xE02B2B,
    )
    await context.send(embed=embed)


async def handle_bot_missing_permissions(context: Context, error) -> None:
    embed = discord.Embed(
        description="I am missing the permission(s) `"
        + ", ".join(error.missing_permissions)
        + "` to fully perform this command!",
        color=0xE02B2B,
    )
    await context.send(embed=embed)


async def handle_missing_required_argument(context: Context, error) -> None:
    embed = discord.Embed(
        title="Error!",
        # We need to capitalize because the command arguments have no capital letter in the code.
        description=str(error).capitalize(),
        color=0xE02B2B,
    )
    await context.send(embed=embed)
