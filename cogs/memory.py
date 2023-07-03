import data
import model

import discord
from discord.ext import commands
from discord import app_commands

async def setup(bot : commands.Bot):
    await bot.add_cog(Memory(bot))

# Cog that mentions all events having to do with sconversation memory
class Memory(commands.Cog):
    bot : commands.Bot
    
    def __init__(self, bot : commands.Bot):
        self.bot = bot
    
    @app_commands.guilds(data.GUILD)
    @app_commands.command(name = "clear_memory", description = "Clear character memory")
    async def clear_memory(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)
        user.currentCharacter.lastQuestion = ""
        user.currentCharacter.conversation = []
        user.currentCharacter.currentConversationCharacters = 0
        embed = discord.Embed(description=f"Cleared {user.currentCharacter.name}'s memory!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

    @app_commands.guilds(data.GUILD)
    @app_commands.command(name = "delete_last_interaction", description = "Delete the last pair of messages")
    async def delete_last_interaction(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)
        user.currentCharacter.lastQuestion = ""
        if len(user.currentCharacter.conversation) > 0:
            b = user.currentCharacter.conversation.pop()
            u = user.currentCharacter.conversation.pop()
            user.currentCharacter.currentConversationCharacters -= len(b) + len(u)
            embed = discord.Embed(title=f"Deleted the following interaction in {user.currentCharacter.name}'s memory:",
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
            options.append(discord.SelectOption(label="No memory", description="Your character will converse without memory entirely."))
            options.append(discord.SelectOption(label="Frozen", description="Your character will converse with previous but no new memory."))
            options.append(discord.SelectOption(label="Conversation", description="Your character will remember 3000 characters of conversation."))
            super().__init__(placeholder='Change mode', min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            await interaction.message.edit(view = None)

            self.targetChar.mode = self.values[0].lower()
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
    @app_commands.guilds(data.GUILD)
    @app_commands.command(name = "change_mode", description = "Change character mode")
    async def change_mode(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)

        if user.characters.index(user.currentCharacter) == 2:
            embed = discord.Embed(description="You can't change the mode of this character!", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            return
        view = self.ChangeModeView(self, user.currentCharacter)
        embed = discord.Embed(description="Select a mode to change your current character to:", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, view=view)