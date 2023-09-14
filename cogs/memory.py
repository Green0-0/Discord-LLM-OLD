import data

import model
import discord
from discord.ext import commands
from discord import app_commands

async def setup(bot : commands.Bot):
    await bot.add_cog(Memory(bot))

# Cog that mentions all events having to do with conversation memory
class Memory(commands.Cog):
    bot : commands.Bot
    
    def __init__(self, bot : commands.Bot):
        self.bot = bot
    
    @app_commands.command(name = "clear_memory", description = "Clear character memory. Lost memory cannot be restored!")
    @app_commands.checks.bot_has_permissions(embed_links=True)
    async def clear_memory(self, interaction : discord.Interaction):
        if interaction.channel in data.threadChar:
            if not (interaction.user == data.threadChar[interaction.channel].owner or interaction.user in data.admins or await self.bot.is_owner(interaction.user)):
                embed = discord.Embed(description="You do not own this thread nor have permissions to clear its memory!", color=discord.Color.yellow())
                await interaction.response.send_message(embed=embed)
                return
            character = data.threadChar[interaction.channel].character
        else:
            user = data.get_user(interaction.user.id) 
            character = user.currentCharacter
        
        character.lastQuestion = ""
        character.conversation = []
        embed = discord.Embed(description=f"Cleared {character.name}'s memory!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name = "delete_last_interaction", description = "Delete the last pair of messages (your query and the bots response) from memory.")
    @app_commands.checks.bot_has_permissions(embed_links=True)
    async def delete_last_interaction(self, interaction : discord.Interaction):
        if interaction.channel in data.threadChar:
            if not (interaction.user == data.threadChar[interaction.channel].owner or interaction.user in data.admins or await self.bot.is_owner(interaction.user)):
                embed = discord.Embed(description="You do not own this thread nor have permissions to delete its memory!", color=discord.Color.yellow())
                await interaction.response.send_message(embed=embed)
                return
            character = data.threadChar[interaction.channel].character
        else:
            user = data.get_user(interaction.user.id) 
            character = user.currentCharacter
        character.lastQuestion = ""
        if len(character.conversation) > 0:
            if interaction.channel in data.threadChar:
                l = character.conversation.pop()
                embed = discord.Embed(title=f"Deleted the following message in {character.name}'s memory:",
                                    description=f"{l}", color=discord.Color.red())
            else:
                b = character.conversation.pop()
                u = character.conversation.pop()
                embed = discord.Embed(title=f"Deleted the following interaction in {character.name}'s memory:",
                                    description=f"{u}\n{b}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(description="No interactions found!", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)

    # A select menu is basically a dropdown where the user has to pick one of the options
    # A select menu that lets the user choose one of their characters to delete 
    class ChangeModeSelectMenu(discord.ui.Select):
        targetChar : model.Character

        def __init__(self, targetChar : model.Character):
            self.targetChar = targetChar
            options = []
            options.append(discord.SelectOption(label="Has memory", description="Your character will remember the conversation (up to its memory length)."))
            options.append(discord.SelectOption(label="No memory", description="Your character will converse with previous but no new memory."))
            super().__init__(placeholder='Change mode', min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            await interaction.message.edit(view = None)

            self.targetChar.memory = self.values[0].lower() == "has memory"
            embed = discord.Embed(description=f"Mode set to {self.values[0].lower()}", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
            self.disabled = True

    # Attaches the above select menu to a view
    class ChangeModeView(discord.ui.View):
        def __init__(self, parent, targetChar : model.Character):
            super().__init__()

            # Adds the dropdown to our view object.
            self.add_item(parent.ChangeModeSelectMenu(targetChar))

    # Links the above view to a slash command
    @app_commands.command(name = "change_memory_mode", description = "Set whether or not the character remembers new conversations")
    @app_commands.checks.bot_has_permissions(embed_links=True)
    async def change_mode(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)

        if user.currentCharacter.name == "Text Completion":
            embed = discord.Embed(description="You can't change the memory mode of this character!", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            return
        view = self.ChangeModeView(self, user.currentCharacter)
        embed = discord.Embed(description="Select a mode to change your current character to:", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, view=view)