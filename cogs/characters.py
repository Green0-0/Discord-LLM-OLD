import data
import model
import requests
import logging

import discord
from discord.ext import commands
from discord import ui, app_commands

async def setup(bot : commands.Bot):
    await bot.add_cog(Characters(bot))

def isFloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    
# Cog that manages all events which require an LLM response
class Characters(commands.Cog):
    bot : commands.Bot
    
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    # A modal is basically a form the user fills out and then submits
    # A modal that creates a new character with a name and icon (unchangable) and a profile (changable)
    class CreateCharacterModal(ui.Modal, title = "Character Creation"):
        name = ui.TextInput(label="Character's name:", 
                            required=True)

        icon = ui.TextInput(label="URL for your character's profile picture:", 
                            placeholder="png, jpeg, or jpg", 
                            default="https://cdn.discordapp.com/embed/avatars/0.png", 
                            required=True)
        
        profile = ui.TextInput(label="Character's profile:", 
                               default="(Recommended to edit this with /edit_profile) CHARACTER is a helpful assistant.", 
                               required=True)
        
        # Called when the user submits the modal
        async def on_submit(self, interaction : discord.Interaction):
            # On the extremely rare chance the user pops open two tabs and tries to make two characters at once to break the limit...
            user = data.get_user(interaction.user.id)
            
            if (len(user.characters) > 24):
                embed = discord.Embed(description="You have reached the character limit! Please delete a character before creating a new one.", color=discord.Color.yellow())
                await interaction.response.send_message(embed=embed)
                embed = discord.Embed(title="Failed to create character " + self.name.value, description="Character description: " + self.profile.value, color=discord.Color.yellow())
                await interaction.channel.send(embed=embed)
                return
            
            # Checks if the icon URL is valid
            try:
                r = requests.head(self.icon.value)
                image_formats = ("image/png", "image/jpeg", "image/jpg")
                if r.headers["content-type"] not in image_formats:
                    embed = discord.Embed(description="Invalid icon URL", color=discord.Color.yellow())
                    await interaction.response.send_message(embed=embed)
                    embed = discord.Embed(title="Failed to create character " + self.name.value, description="Character description: " + self.profile.value, color=discord.Color.yellow())
                    await interaction.channel.send(embed=embed)
                    return
            except:
                embed = discord.Embed(description="Invalid icon URL", color=discord.Color.yellow())
                await interaction.response.send_message(embed=embed)
                embed = discord.Embed(title="Failed to create character " + self.name.value, description="Character description: " + self.profile.value, color=discord.Color.yellow())
                await interaction.channel.send(embed=embed)
                return
            
            # Adds character to user character list and sets it to the current character, also attaches some default values to model parameters
            user = data.get_user(interaction.user.id)

            user.modelUniqueID += 1
            newCharacter = model.Character(user.modelUniqueID, self.name.value, self.icon.value, data.LLMModels[0], temperature=1.4)
            newCharacter.setProfile(self.profile.value)
            user.currentCharacter = newCharacter
            user.characters.append(newCharacter)

            embed = discord.Embed(title=newCharacter.name, 
                                      description=newCharacter.profile,
                                      color=discord.Color.blue())
            embed.set_author(name="Created")
            embed.set_footer(text="Mention the bot with @LLM followed by a message to begin chatting with the character!")
            embed.set_thumbnail(url=newCharacter.icon)

            await interaction.response.send_message(embed=embed)
            
    # Links the modal above to a slash command
    @app_commands.command(name = "create_character", description = "Create a new character. Simply give a name, icon, and description/profile.")
    @app_commands.checks.bot_has_permissions(embed_links=True)
    async def create_character_command(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)

        # There is a limit to the size of dropdown menus which I use for switching characters
        if (len(user.characters) > 24):
            embed = discord.Embed(description="You have reached the character limit! Please delete a character before creating a new one.", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            return
        await interaction.response.send_modal(self.CreateCharacterModal())

    @app_commands.command(name = "quick_create_character", description = "Create a new character without the popup menu.")
    @app_commands.checks.bot_has_permissions(embed_links=True)
    async def quick_create_character_command(self, interaction : discord.Interaction, name : str, icon : str = "https://cdn.discordapp.com/embed/avatars/0.png", profile : str = ""):
        user = data.get_user(interaction.user.id)

        # There is a limit to the size of dropdown menus which I use for switching characters
        if (len(user.characters) > 24):
            embed = discord.Embed(description="You have reached the character limit! Please delete a character before creating a new one.", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            embed = discord.Embed(title="Failed to create character " + name, description="Character description: " + profile, color=discord.Color.yellow())
            await interaction.channel.send(embed=embed)
            return
        
        # Checks if the icon URL is valid
        try:
            r = requests.head(icon)
            image_formats = ("image/png", "image/jpeg", "image/jpg")
            if r.headers["content-type"] not in image_formats:
                embed = discord.Embed(description="Invalid icon URL", color=discord.Color.yellow())
                await interaction.response.send_message(embed=embed)
                embed = discord.Embed(title="Failed to create character " + name, description="Character description: " + profile, color=discord.Color.yellow())
                await interaction.channel.send(embed=embed)
                return
        except:
            embed = discord.Embed(description="Invalid icon URL", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            embed = discord.Embed(title="Failed to create character " + name, description="Character description: " + profile, color=discord.Color.yellow())
            await interaction.channel.send(embed=embed)
            return
        
        # Adds character to user character list and sets it to the current character, also attaches some default values to model parameters
        user = data.get_user(interaction.user.id)

        user.modelUniqueID += 1
        newCharacter = model.Character(user.modelUniqueID, name, icon, data.LLMModels[0], temperature=1.4)
        newCharacter.setProfile(profile)
        user.currentCharacter = newCharacter
        user.characters.append(newCharacter)

        embed = discord.Embed(title=newCharacter.name, 
                                    description=newCharacter.profile,
                                    color=discord.Color.blue())
        embed.set_author(name="Created")
        embed.set_footer(text="Mention the bot with @LLM followed by a message to begin chatting with the character!")
        embed.set_thumbnail(url=newCharacter.icon)

        await interaction.response.send_message(embed=embed)


    # A modal that edits the properties (temp, top_p, len, etc) of a character
    class ConfigModal(ui.Modal, title = "Set Properties"):
        targetChar : model.Character

        def __init__(self, targetChar : model.Character):
            super().__init__()
            self.targetChar = targetChar
            self.add_item(discord.ui.TextInput(label="Temperature:", 
                                               default=str(targetChar.temperature), 
                                               placeholder="Lower value = more consistent, less randomness", 
                                               required=True))
            
            self.add_item(discord.ui.TextInput(label="Top_p:", 
                                               default=str(targetChar.top_p), 
                                               placeholder="Higher value = larger range of possible random results", 
                                               required=True))
            
            self.add_item(discord.ui.TextInput(label="Top_k:", 
                                               default=str(targetChar.top_k), 
                                               placeholder="Higher value = larger range of possible random results", 
                                               required=True))
            
            self.add_item(discord.ui.TextInput(label="Repetition_penalty:", 
                                               default=str(targetChar.repetition_penalty), 
                                               placeholder="Higher value = less repetition", 
                                               required=True))
            
            self.add_item(discord.ui.TextInput(label="Max_length:", 
                                               default=str(targetChar.max_new_len), 
                                               placeholder="Higher value = longer possible results", 
                                               required=True))
            
        async def on_submit(self, interaction : discord.Interaction):
            # Checks if the input is valid floats or ints
            if isFloat(self.children[0].value) and isFloat(self.children[1].value) and self.children[2].value.isdigit() and isFloat(self.children[3].value) and self.children[4].value.isdigit():                
                embed = discord.Embed(title=f"Modified {self.targetChar.name}'s Properties", 
                                      description=f""" temperature: {self.targetChar.temperature} -> {self.children[0].value}
                                           top_p: {self.targetChar.top_p} -> {self.children[1].value}
                                           top_k: {self.targetChar.top_k} -> {self.children[2].value}
                                           repetition_penalty: {self.targetChar.repetition_penalty} -> {self.children[3].value}
                                           max_new_len: {self.targetChar.max_new_len} -> {self.children[4].value}""",
                                      color=discord.Color.blue())
                embed.set_thumbnail(url=self.targetChar.icon)

                self.targetChar.temperature = float(self.children[0].value)
                self.targetChar.top_p = float(self.children[1].value)
                self.targetChar.top_k = int(self.children[2].value)
                self.targetChar.repetition_penalty = float(self.children[3].value)
                self.targetChar.max_new_len = int(self.children[4].value)
                await interaction.response.send_message(embed=embed)
            else: 
                embed = discord.Embed(description="Invalid input!", color=discord.Color.yellow())
                await interaction.response.send_message(embed=embed)
                return
    
    # Links the above modal to a slash command
    @app_commands.command(name = "config", description = "Configure your character's properties, like temperature, length, etc.")
    @app_commands.checks.bot_has_permissions(embed_links=True)
    async def config_command(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)
        await interaction.response.send_modal(self.ConfigModal(user.currentCharacter))

    # A modal that edits the profile (system prompt) of a character
    class EditProfileModal(ui.Modal, title = "Edit Profile"):
        targetChar : model.Character

        def __init__(self, targetChar : model.Character):
            super().__init__()
            self.targetChar = targetChar
            self.add_item(discord.ui.TextInput(label="Describe your character.", 
                                               placeholder="Female? Male? Likes music? Relationship with the user?", 
                                               default=targetChar.profile, 
                                               required=True))
            
            self.add_item(discord.ui.TextInput(label="How do the character and user interact?", 
                                               placeholder="Are they helpful, annoyed, and will they have censorship?", 
                                               required=False))
            
            self.add_item(discord.ui.TextInput(label="Give some examples character responses.", 
                                               placeholder="\"Tysm!! :) ^^\", \"Annoying, go away...\", etc", 
                                               required=False))
            
            self.add_item(discord.ui.TextInput(label="Anything else?", 
                                               required=False))

        async def on_submit(self, interaction : discord.Interaction):
            newProfile = self.children[0].value + (" " if self.children[1].value != "" else "") + self.children[1].value + (" " if self.children[2].value != "" else "") + self.children[2].value + (" " if self.children[3].value != "" else "") + self.children[3].value
            self.targetChar.setProfile(newProfile)
            embed = discord.Embed(title=f"Changed {self.targetChar.name}'s Profile to:", description=newProfile, color=discord.Color.blue())
            embed.set_thumbnail(url=self.targetChar.icon)
            await interaction.response.send_message(embed=embed)

    # Links the above modal to a slash command
    @app_commands.command(name = "edit_profile", description = "Edit your current character's profile. This gives it its personality.")
    @app_commands.checks.bot_has_permissions(embed_links=True)
    async def edit_profile(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)

        if user.currentCharacter.name == "Text Completion":
            embed = discord.Embed(description="You can't change the profile of this characters!", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            return
        await interaction.response.send_modal(self.EditProfileModal(user.currentCharacter))

    # A select menu is basically a dropdown where the user has to pick one of the options
    # A select menu that lets the user choose one of their characters to delete 
    class ChangeModelSelectMenu(discord.ui.Select):
        targetChar : model.Character

        def __init__(self, targetChar : model.Character):
            self.targetChar = targetChar
            options = []
            for m in data.LLMModels:
                options.append(discord.SelectOption(label=m.displayName, description=m.displayDescription))
            super().__init__(placeholder='Change model', min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            await interaction.message.edit(view = None)

            for m in data.LLMModels:
                if m.displayName == self.values[0]:
                    self.targetChar.model = m
                    embed = discord.Embed(description=f"Now using {self.values[0]}", color=discord.Color.blue())
                    await interaction.response.send_message(embed=embed)
                    self.disabled = True
                    return
            embed = discord.Embed(description=f"Model {self.values[0]} not found?", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            logging.error(f"<ERROR> Model {self.values[0]} not found")

    # Attaches the above select menu to a view
    class ChangeModelView(discord.ui.View):
        def __init__(self, parent, targetChar : model.Character):
            super().__init__()

            # Adds the dropdown to our view object.
            self.add_item(parent.ChangeModelSelectMenu(targetChar))

    # Links the above view to a slash command
    @app_commands.command(name = "change_model", description = "Change the AI LLM model used to generate character outputs")
    @app_commands.checks.bot_has_permissions(embed_links=True)
    async def change_model(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)
        view = self.ChangeModelView(self, user.currentCharacter)
        embed = discord.Embed(description="Select a model to use on this character:", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, view=view)

    # A select menu is basically a dropdown where the user has to pick one of the options
    # A select menu that lets the user choose one of their characters to delete 
    class DeleteCharacterSelectMenu(discord.ui.Select):
        originalLen : int

        def __init__(self, characters : list):
            self.originalLen = len(characters)
            options = []
            for i in range (len(characters)):
                options.append(discord.SelectOption(label=i, description=characters[i].name))

            super().__init__(placeholder='Select a character to delete', min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            await interaction.message.edit(view = None)

            user = data.get_user(interaction.user.id)

            if (self.originalLen != len(user.characters)):
                embed = discord.Embed(description="Character list was changed, aborting deletion...", color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                return
            c = user.characters[int(self.values[0])]
            if c == user.currentCharacter:
                embed = discord.Embed(description="You can't delete the current character!", color=discord.Color.yellow())
                await interaction.response.send_message(embed=embed)
                return
            user.characters.remove(c)
            
            embed = discord.Embed(title=c.name, 
                                      description=c.profile,
                                      color=discord.Color.red())
            embed.set_author(name="Deleted")
            embed.set_thumbnail(url=c.icon)

            await interaction.response.send_message(embed=embed)
            self.disabled = True

    # Attaches the above select menu to a view
    class DeleteCharacterView(discord.ui.View):
        def __init__(self, parent, characters : list):
            super().__init__()

            # Adds the dropdown to our view object.
            self.add_item(parent.DeleteCharacterSelectMenu(characters))

    # Links the above view to a slash command
    @app_commands.command(name = "delete_character", description = "Delete a character. This cannot be undone! (Though you can just remake it.)")
    @app_commands.checks.bot_has_permissions(embed_links=True)
    async def delete_character(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)
        if len(user.characters) < 2:
            embed = discord.Embed(description="Please do not delete any more characters!", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            return
        view = self.DeleteCharacterView(self, user.characters)
        embed = discord.Embed(description="Select a character to delete:", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, view=view)



