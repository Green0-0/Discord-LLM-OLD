import discord
from discord.ext import commands
import data 
import logging
import logging
from io import StringIO

log_stream = StringIO()    
logger = logging.basicConfig(stream=log_stream, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())
data.init(log_stream)

class LLM (commands.Bot):
    async def setup_hook(self):
        logging.info("Bot is starting")
        await bot.load_extension("cogs.generics")
        await self.tree.sync()

# Sets up bot
intents = discord.Intents.default()
intents.message_content = True
bot = LLM(command_prefix="", intents=intents, help_command=None)

# Finishes setting up the bot
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.watching, name="/reload must be used by an admin before this bot does anything!"))
    logging.info(f'Logged in as {bot.user}, begin using the bot!')

bot.run(data.TOKEN, log_handler=logger)