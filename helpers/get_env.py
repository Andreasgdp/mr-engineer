import os

from dotenv import load_dotenv

load_dotenv()

# create object of env
env = os.environ


class Env:
    def __init__(self):
        self.prefix = str(env.get("PREFIX"))
        self.token = str(env.get("DISCORD_TOKEN"))
        self.bot_permissions = str(env.get("BOT_PERMISSIONS"))
        self.application_id = str(env.get("APPLICATION_ID"))

    def __str__(self):
        return f"Env(prefix={self.prefix}, token={self.token}, bot_permissions={self.bot_permissions}, application_id={self.application_id})"
