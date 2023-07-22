"""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import asyncio
import json
import os
import platform
import random
import sys

import aiosqlite
import discord
from cogwatch import Watcher  # pylint: disable=import-error
from discord.ext import commands, tasks
from discord.ext.commands import Context

import exceptions
from helpers import cmd_err_handlers, get_env
from helpers.get_logger import logger
from helpers.mr_engineer_bot import MrEngineer
from keep_alive import keep_alive

env = get_env.Env()

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(
        f"{os.path.realpath(os.path.dirname(__file__))}/config.json", encoding="utf-8"
    ) as file:
        config = json.load(file)


bot = MrEngineer()
bot.logger = logger
bot.config = config


async def init_db():
    async with aiosqlite.connect(
        f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
    ) as database:
        with open(
            f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql",
            encoding="utf-8",
        ) as db_schema_file:
            await database.executescript(db_schema_file.read())
        await database.commit()


@bot.event
async def on_ready() -> None:
    """
    The code in this event is executed when the bot is ready.
    """
    watcher = Watcher(bot, path="cogs", preload=True, debug=False)
    await watcher.start()
    assert bot.user is not None
    bot.logger.info("Logged in as %s", bot.user.name)
    bot.logger.info("discord.py API version: %s", discord.__version__)
    bot.logger.info("Python version: %s", platform.python_version())
    bot.logger.info(
        "Running on: %s %s (%s)", platform.system(), platform.release(), os.name
    )
    bot.logger.info("-------------------")
    status_task.start()
    if config["sync_commands_globally"]:
        bot.logger.info("Syncing commands globally...")
        await bot.tree.sync()


@tasks.loop(minutes=1.0)
async def status_task() -> None:
    """
    Setup the game status task of the bot.
    """
    statuses = ["with you!", "with Krypton!", "with humans!"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    The code in this event is executed every time someone sends a message, with or without the prefix

    :param message: The message that was sent.
    """
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)


@bot.event
async def on_command_completion(context: Context) -> None:
    """
    The code in this event is executed every time a normal command has been *successfully* executed.

    :param context: The context of the command that has been executed.
    """
    assert context.command is not None
    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    if context.guild is not None:
        bot.logger.info(
            "Executed %s command in %s (ID: %s) by %s (ID: %s)",
            executed_command,
            context.guild.name,
            context.guild.id,
            context.author,
            context.author.id,
        )
    else:
        bot.logger.info(
            "Executed %s command by %s (ID: %s)",
            executed_command,
            context.author,
            context.author.id,
        )


@bot.event
async def on_command_error(context: Context, error) -> None:
    """
    The code in this event is executed every time a normal valid command catches an error.

    :param context: The context of the normal command that failed executing.
    :param error: The error that has been faced.
    """
    if isinstance(error, commands.CommandOnCooldown):
        await cmd_err_handlers.handle_command_on_cooldown(context, error)
    elif isinstance(error, exceptions.UserBlacklisted):
        await cmd_err_handlers.handle_user_blacklisted(context, bot)
    elif isinstance(error, exceptions.UserNotOwner):
        await cmd_err_handlers.handle_user_not_owner(context, bot)
    elif isinstance(error, commands.MissingPermissions):
        await cmd_err_handlers.handle_missing_permissions(context, error)
    elif isinstance(error, commands.BotMissingPermissions):
        await cmd_err_handlers.handle_bot_missing_permissions(context, error)
    elif isinstance(error, commands.MissingRequiredArgument):
        await cmd_err_handlers.handle_missing_required_argument(context, error)
    else:
        raise error


async def load_cogs() -> None:
    """
    The code in this function is executed whenever the bot will start.
    """
    for cog_file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
        if cog_file.endswith(".py"):
            extension = cog_file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                bot.logger.info("Loaded extension %s", extension)
            except Exception as ex:
                exception = f"{type(ex).__name__}: {ex}"
                bot.logger.error(
                    "Failed to load extension %s\n%s", extension, exception
                )


asyncio.run(init_db())
asyncio.run(load_cogs())
keep_alive()

try:
    bot.run(str(bot.env.token))
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    os.system("kill 1")
    os.system("python restarter.py")
