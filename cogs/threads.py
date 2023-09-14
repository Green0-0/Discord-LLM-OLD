import data
import model
import discord
from discord.ext import commands
from discord import app_commands

async def setup(bot : commands.Bot):
    await bot.add_cog(Threads(bot))

# Cog that allows the creation of character channels, where a character can be talked to by multiple users
class Threads(commands.Cog):
    bot : commands.Bot
    
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @app_commands.command(name = "create_thread", description = "Create a new character thread with your currently selected character.")
    @app_commands.checks.bot_has_permissions(embed_links=True, manage_threads=True)
    async def create_thread(self, interaction : discord.Interaction):
        if isinstance(interaction.channel, discord.Thread):
            embed = discord.Embed(description="This cannot be done in a thread!", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            return
        if isinstance(interaction.channel, discord.DMChannel):
            embed = discord.Embed(description="This cannot be done in DMs!", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            return
        
        user = data.get_user(interaction.user.id)
        c = model.Character(-1, user.currentCharacter.name, user.currentCharacter.icon, user.currentCharacter.model, memory=user.currentCharacter.memory,
                            temperature=user.currentCharacter.temperature, top_p = user.currentCharacter.top_p, top_k = user.currentCharacter.top_k, repetition_penalty = user.currentCharacter.repetition_penalty, max_new_len=user.currentCharacter.max_new_len, 
                            multiUser=True)
        c.setProfile(user.currentCharacter.profile)

        embed = discord.Embed(title=f"Thread for {c.name}", description=f"Note: All slash commands besides /delete_thread, /view_current_character, /clear_memory, /delete_last_interaction and /reply_as_current will not do anything in this thread!", color=discord.Color.blue())
        msg = await interaction.channel.send(embed=embed)
        thread = CharacterThread(await msg.create_thread(name="Chat with " + c.name),
                                    interaction.user, c)
        data.threadChar[thread.thread] = thread
        await interaction.response.send_message("Done!")

    @app_commands.command(name = "delete_thread", description = "Delete a character thread (you can only do this to your own character thread).")
    @app_commands.checks.bot_has_permissions(embed_links=True, manage_threads=True)
    async def delete_channel(self, interaction : discord.Interaction):
        if not interaction.channel in data.threadChar:
            embed = discord.Embed(description="Thread not found!", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            return
        
        if not (interaction.user == data.threadChar[interaction.channel].owner or interaction.user in data.admins or await self.bot.is_owner(interaction.user)):
            embed = discord.Embed(description="You do not own this thread nor have permissions to delete it!", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            return
        
        await interaction.response.send_message("Done!")
        t = data.threadChar.pop(interaction.channel).thread
        await t.edit(archived=True)

class CharacterThread:
    thread : discord.Thread
    owner : discord.User
    character : model.Character

    def __init__(self, channel : discord.Thread, owner : discord.User, character : model.Character):
        self.thread = channel
        self.owner = owner
        self.character = character