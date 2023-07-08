import model as m

import discord
from discord import ui, app_commands
from discord.ext import commands
import data 

class LLM (commands.Bot):
    async def setup_hook(self):
        print("Bot is starting")
        await bot.load_extension("cogs.management")
        await bot.load_extension("cogs.memory")
        await bot.load_extension("cogs.messaging")
        await bot.load_extension("cogs.characters")
        print ("Bot is loaded")

# Sets up bot

intents = discord.Intents.default()
intents.message_content = True
bot = LLM(command_prefix=".", intents=intents)

data.init()

# Finishes setting up the bot
@bot.event
async def on_ready():
    guild = await bot.fetch_guild(data.GUILD)
    await bot.tree.sync()
    for w in await guild.webhooks():
        await w.delete()
    print(f'Logged in as {bot.user}, begin using the bot!')
    
bot.run(data.TOKEN)