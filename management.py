import data

import discord
from discord.ext import commands
from discord import app_commands

async def setup(bot : commands.Bot):
    await bot.add_cog(Management(bot))

class Management(commands.Cog):
    bot : commands.Bot

    def __init__(self, bot : commands.Bot):
        self.bot = bot

    # A select menu is basically a dropdown where the user has to pick one of the options
    # A select menu that lets the user choose one of their characters to talk to
    class SelectCharacter_selectmenu(discord.ui.Select):
        originalLen : int

        def __init__(self, characters : list):
            self.originalLen = len(characters)
            options = []
            for i in range (len(characters)):
                options.append(discord.SelectOption(label=i, description=characters[i].name))

            super().__init__(placeholder='Select a character', min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            await interaction.message.edit(view = None)

            user = data.get_user(interaction.user.id)
            if (self.originalLen != len(user.characters)):
                embed = discord.Embed(description="Character list was changed, aborting selection...", color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                return

            user.currentCharacter = user.characters[int(self.values[0])]
            if len(user.currentCharacter.conversation) == 0:
                embed = discord.Embed(title=user.currentCharacter.name, description=f"Begin a new conversation with {user.currentCharacter.name} by mentioning the bot with @LLM!", color=discord.Color.blue())
                embed.set_author(name="Selected")
                embed.set_thumbnail(url=user.currentCharacter.icon)
                await interaction.response.send_message(embed=embed)
            else:
                embed = discord.Embed(title=user.currentCharacter.name, description=f"\nContinue the conversation with {user.currentCharacter.name} by mentioning the bot with @LLM!", color=discord.Color.blue())
                embed.set_author(name="Selected")
                embed.set_thumbnail(url=user.currentCharacter.icon)
                await interaction.response.send_message(embed=embed)
            self.disabled = True

    # Attaches the above select menu to a view
    class SelectCharacterView(discord.ui.View):
        def __init__(self, parent, characters : list):
            super().__init__()

            # Adds the dropdown to our view object.
            self.add_item(parent.SelectCharacter_selectmenu(characters))

    # Links the above view to a slash command
    @app_commands.command(name = "change_character", description = "Change to a different character profile.")
    @app_commands.checks.bot_has_permissions(embed_links=True)
    async def change_character(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)
        view = self.SelectCharacterView(self, user.characters)
        embed = discord.Embed(description="Select a character:", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name = "list_characters", description = "List all the characters that you've created.")
    @app_commands.checks.bot_has_permissions(embed_links=True)
    async def list_characters(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)
        charList = "\n".join([character.name for character in user.characters])
        embed = discord.Embed(title="Characters", description=charList, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name = "view_current_character", description = "View your currently selected character, its properties, profile, and conversations.")
    @app_commands.checks.bot_has_permissions(embed_links=True)
    async def view_current_character(self, interaction : discord.Interaction):
        if interaction.channel in data.threadChar:
            character = data.threadChar[interaction.channel].character
        else:
            user = data.get_user(interaction.user.id)
            character = user.currentCharacter
        embed = discord.Embed(title=character.name, description="Remember new messages?: " + str(character.memory) + "\n" + character.profile, color=discord.Color.blue())
        embed.set_thumbnail(url=character.icon)
        await interaction.response.send_message(embed=embed)
        embed = discord.Embed(title="Properties", description="Temperature: " + str(character.temperature) + "\n" + "Top_p: " + str(character.top_p) + "\n" + "Top_k: " + str(character.top_k) + "\n" + "Repetition Penalty: " + str(character.repetition_penalty) + "\n" + "Max Length: " + str(character.max_new_len), color=discord.Color.blue())
        await interaction.channel.send(embed=embed)
        convo = "\n".join(character.conversation)
        if (len(convo) > 4000):
            # write to file
            with open("Conversation_History.txt", "w") as file:
                file.write(convo)
            
            # send file to Discord in message
            with open("Conversation_History.txt", "rb") as file:
                await interaction.channel.send("Conversation History:", file=discord.File(file, "Conversation_History.txt"))
        else:
            embed = discord.Embed(title="Conversation History", description=convo, color=discord.Color.blue())
            await interaction.channel.send(embed=embed)
