import Model as m

import validators
import requests
import typing
import random
import discord
from discord import ui, app_commands

# Sets up bot
TOKEN = "MTEyNDQ3ODE5NzczNjY4OTY5NA.G9kREQ.4Dl9Fxj7y9manpo2By9VxG-Zm4CUb5bp0AoCyE"
GUILD = "1124478446492471426"

SuggestionModel = m.Character(0, "no memory", "Airoboros", "https://cdn.discordapp.com/embed/avatars/0.png", 0, 1.7, 0.95, 50, 1.2, 4000)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Cache info to save memory and user configurations
users_cache = {}
webhooks_cache = {}

######### Helper functions, might be better in a separate file
# Sends a message in a given channel while roleplaying as a character
async def sendCharacterMessage(channel, userid, message, model):
    # Webhooks do not work in dm, so roleplay is not possible. Simply sends the message.
    if isinstance(channel, discord.DMChannel):
        await channel.send(model.name + ": " + message)
    else: 
        # Tries to find a webhook from the cache, if not found uses a new one.
        webhooktag = str(userid) + " " + str(channel.id) + " " + str(model.id)
        if webhooktag not in webhooks_cache:
            print("Generated new webhook")
            avatar = requests.get(model.icon).content
            # If there isn't enough space for the new webhook (discord has a webhook limit), delete one from the cache
            if len(webhooks_cache) > 9:
                await webhooks_cache.pop(0).delete()
            webhook = await channel.create_webhook(name=model.name, avatar=avatar)
            
            webhooks_cache[webhooktag] = webhook 
        else:
            print("Used cached webhook")
            webhook = webhooks_cache[webhooktag]
        # Sends the message using the webhook
        await webhook.send(str(message))

# For parsing user input for things like temperature, top_p, etc
def isFloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Gets a user from the cache
def getUser(user):
    if user in users_cache:
        return users_cache[user]
    else:
        newUser = m.User()
        users_cache[user] = newUser
        return newUser
#########

# The modal/form for character creation
class create_character_modal(ui.Modal, title = "Character Creation"):
    # Fields, with some default values
    name = ui.TextInput(label="Character's name:", required=True)
    icon = ui.TextInput(label="URL for your character's profile picture:", placeholder="png or jpg", default="https://cdn.discordapp.com/embed/avatars/0.png", required=True)
    profile = ui.TextInput(label="Character's profile:", default="(Recommended to edit this with /edit_profile) CHARACTER is a helpful assistant.", required=True)

    async def on_submit(self, interaction : discord.Interaction):
        # Checks if the icon URL is valid
        await interaction.response.defer()
        if not validators.url(self.icon.value):
            await interaction.response.send_message("Invalid icon URL")
            return
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        r = requests.head(self.icon)
        if r.headers["content-type"] not in image_formats:
            await interaction.response.send_message("Invalid icon URL")
            return
        # Adds character to user character list and sets it to the current character, also attaches some default values to model parameters
        user = getUser(interaction.user)
        user.id += 1
        newCharacter = m.Character(user.id, "conversation", self.name.value, self.icon.value, 0, 1.7, 0.95, 50, 1.2, 1500)
        newCharacter.setProfile(self.profile.value)
        user.currentCharacter = newCharacter
        user.characters.append(newCharacter)
        await sendCharacterMessage(interaction.channel, interaction.user.id, "Created character named " + newCharacter.name + " with icon " + newCharacter.icon + " and profile ```" + newCharacter.profile + "```", newCharacter)

# note that the current character could change while editing properties and cause a different character to be edited, this shouldn't happen though
class edit_character_properties(ui.Modal, title = "Set Properties"):
    targetChar : m.Character
    def __init__(self, targetChar):
        super().__init__()
        self.targetChar = targetChar
        self.add_item(discord.ui.TextInput(label="Temperature:", default=str(targetChar.temperature), placeholder="Lower value = more consistent, less randomness", required=True))
        self.add_item(discord.ui.TextInput(label="Top_p:", default=str(targetChar.top_p), placeholder="Higher value = larger range of possible random results", required=True))
        self.add_item(discord.ui.TextInput(label="Top_k:", default=str(targetChar.top_k), placeholder="Higher value = larger range of possible random results", required=True))
        self.add_item(discord.ui.TextInput(label="Repetition_penalty:", default=str(targetChar.repetition_penalty), placeholder="Higher value = less repetition", required=True))
        self.add_item(discord.ui.TextInput(label="Max_length:", default=str(targetChar.max_new_len), placeholder="Higher value = longer possible results", required=True))
        
    async def on_submit(self, interaction : discord.Interaction):
        # Checks if the input is valid floats or ints
        if isFloat(self.children[0].value) and isFloat(self.children[1].value) and self.children[2].value.isdigit() and isFloat(self.children[3].value) and self.children[4].value.isdigit():
            await interaction.response.defer()
            self.targetChar.temperature = float(self.children[0].value)
            self.targetChar.top_p = float(self.children[1].value)
            self.targetChar.top_k = int(self.children[2].value)
            self.targetChar.repetition_penalty = float(self.children[3].value)
            self.targetChar.max_new_len = int(self.children[4].value)
            await sendCharacterMessage(interaction.channel, interaction.user.id, "Modified character properties: temperature = " + str(self.targetChar.temperature) + ", " + "top_p = " + str(self.targetChar.top_p) + ", " + "top_k = " + str(self.targetChar.top_k) + ", " + "repetition_penalty = " + str(self.targetChar.repetition_penalty) + ", " + "max_new_len = " + str(self.targetChar.max_new_len), self.targetChar)

        else: 
            await interaction.response.send_message("Invalid input")
            return
        
@tree.command(name = "create_character", description = "Create a new character", guild=discord.Object(GUILD))
async def create_character_command(interaction : discord.Interaction):
    user = getUser(interaction.user)
    if (len(user.characters) > 24):
        await interaction.response.send_message("You have reached the character limit!")
        return
    await interaction.response.send_modal(create_character_modal())

@tree.command(name = "edit_properties", description = "Edit temperature, maxlen, etc", guild=discord.Object(GUILD))
async def edit_properties_command(interaction : discord.Interaction):
    user = getUser(interaction.user)
    await interaction.response.send_modal(edit_character_properties(user.currentCharacter))

@tree.command(name = "clear_memory", description = "Clear character memory", guild=discord.Object(GUILD))
async def clear_memory(interaction : discord.Interaction):
    user = getUser(interaction.user)
    user.currentCharacter.lastQuestion = ""
    user.currentCharacter.conversation = []
    user.currentCharacter.currentConversationCharacters = 0
    await interaction.response.send_message("Cleared character memory!")

@tree.command(name = "delete_last_interaction", description = "Delete the last pair of messages", guild=discord.Object(GUILD))
async def delete_last_interaction(interaction : discord.Interaction):
    user = getUser(interaction.user)
    user.currentCharacter.lastQuestion = ""
    if len(user.currentCharacter.conversation) > 0:
        b = user.currentCharacter.conversation.pop()
        u = user.currentCharacter.conversation.pop()
        user.currentCharacter.currentConversationCharacters -= len(b) + len(u)
        await interaction.response.send_message("Removed the latest  user, model interaction pair. ```" + f"{u} \n{b}```")
    else:
        await interaction.response.send_message("No interactions found!")
    
@tree.command(name = "retry_last_interaction", description = "Retry the last interaction", guild=discord.Object(GUILD))
async def retry_last_interaction(interaction : discord.Interaction):
    user = getUser(interaction.user)
    if user.currentCharacter.lastQuestion != "":
        if user.currentCharacter.conversation[-2] == f"USER: {user.currentCharacter.lastQuestion}":
            user.currentCharacter.currentConversationCharacters -= len(user.currentCharacter.conversation.pop()) + len(user.currentCharacter.conversation.pop())
            await interaction.response.defer()
            async with interaction.channel.typing():
                # Respond to the user message
                response = await user.currentCharacter.request(user.currentCharacter.lastQuestion)
                # Split up response if it is longer than 2k chars
                if (len(response) > 2000):
                    for i in range ((int(len(response)/2000)) + 1):
                        await sendCharacterMessage(interaction.channel, interaction.user.id, response[i*2000:i*2000+2000], user.currentCharacter)
                else:
                    await sendCharacterMessage(interaction.channel, interaction.user.id, response, user.currentCharacter)
        else:
            await interaction.response.send_message("Unable to find last interaction.")
    else:
        await interaction.response.send_message("No interaction found!")

@tree.command(name = "character_suggestions", description = "Get suggestions for your character's profile!", guild=discord.Object(GUILD))
async def retry_last_interaction(interaction : discord.Interaction):
    user = getUser(interaction.user)
    await interaction.response.defer()
    async with interaction.channel.typing():
        # Respond to the user message
        response = await SuggestionModel.request(f"I am trying to write a character named \"{user.currentCharacter.name}\". Currently, I have their profile described as such: \"{user.currentCharacter.profile.replace('CHARACTER', user.currentCharacter.name)}\". How can I improve upon this profile? How can I make it more interesting, unique, and complete in terms of personality? How can I improve the range and quality of interactions this character might have with someone else? Please also provide some examples of things this character might say. Make sure to answer all the questions above with an in depth description/response.")
        # Split up response if it is longer than 2k chars
        if (len(response) > 2000):
            for i in range ((int(len(response)/2000)) + 1):
                print("slicing response")
                await sendCharacterMessage(interaction.channel, interaction.user.id, response[i*2000:i*2000+2000], user.currentCharacter)
        else:
            await sendCharacterMessage(interaction.channel, interaction.user.id, response, user.currentCharacter)

class selectcharacterdropdown(discord.ui.Select):
    def __init__(self, characters : list):
        options = []
        for i in range (len(characters)):
            options.append(discord.SelectOption(label=i, description=characters[i].name))

        super().__init__(placeholder='Select a character', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.edit(view = None)
        user = getUser(interaction.user)
        user.currentCharacter = user.characters[int(self.values[0])]
        await sendCharacterMessage(interaction.channel, interaction.user.id, "Selected character " + user.currentCharacter.name, user.currentCharacter)
        self.disabled = True

class DropdownView(discord.ui.View):
    def __init__(self, characters : list):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(selectcharacterdropdown(characters))

@tree.command(name = "change_character", description = "Change character", guild=discord.Object(GUILD))
async def change_character(interaction : discord.Interaction):
    user = getUser(interaction.user)
    view = DropdownView(user.characters)
    await interaction.response.send_message("Select a character", view=view)

class deletecharacterdropdown(discord.ui.Select):
    def __init__(self, characters : list):
        options = []
        for i in range (len(characters)):
            options.append(discord.SelectOption(label=i, description=characters[i].name))

        super().__init__(placeholder='Select a character to delete', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user = getUser(interaction.user)
        c = user.characters[int(self.values[0])]
        if c == user.currentCharacter:
            await interaction.response.send_message("You can't delete the current character!")
            return
        if int(self.values[0]) < 3:
            await interaction.response.send_message("Please don't delete the default characters!")
            return
        user.characters.remove(c)
        await interaction.message.edit(view = None)
        await sendCharacterMessage(interaction.channel, interaction.user.id, "Deleted character " + c.name + " with avatar " + c.icon + " and profile ```" + c.profile + "```", user.currentCharacter)
        self.disabled = True

class DropdownView2(discord.ui.View):
    def __init__(self, characters : list):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(deletecharacterdropdown(characters))

@tree.command(name = "delete_character", description = "Delete a character", guild=discord.Object(GUILD))
async def delete_character(interaction : discord.Interaction):
    user = getUser(interaction.user)
    view = DropdownView2(user.characters)
    await interaction.response.send_message("Select a character to delete", view=view)

class changeModeDropdown(discord.ui.Select):
    def __init__(self, characters : list):
        options = []
        options.append(discord.SelectOption(label="No memory", description="Your character will converse without memory entirely."))
        options.append(discord.SelectOption(label="Frozen", description="Your character will converse with previous but no new memory."))
        options.append(discord.SelectOption(label="Conversation", description="Your character will remember 3000 characters of conversation."))
        super().__init__(placeholder='Change mode', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.edit(view = None)
        user = getUser(interaction.user)
        if self.values[0] == "No memory":
            user.currentCharacter.mode = "no memory"
            await interaction.channel.send("Mode set to no memory")
        elif self.values[0] == "Frozen":
            user.currentCharacter.mode = "frozen"
            await interaction.channel.send("Mode set to frozen")
        elif self.values[0] == "Conversation":
            user.currentCharacter.mode = "conversation"
            await interaction.channel.send("Mode set to conversation")
        self.disabled = True

class DropdownView3(discord.ui.View):
    def __init__(self, characters : list):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(changeModeDropdown(characters))

@tree.command(name = "change_mode", description = "Change character mode", guild=discord.Object(GUILD))
async def change_mode(interaction : discord.Interaction):
    user = getUser(interaction.user)
    if user.characters.index(user.currentCharacter) == 2:
        await interaction.response.send_message("You can't change the mode of this character!")
        return
    view = DropdownView3(user.characters)
    await interaction.response.send_message("Select a mode to change your current character to", view=view)

@tree.command(name = "list_characters", description = "List characters", guild=discord.Object(GUILD))
async def list_characters(interaction : discord.Interaction):
    user = getUser(interaction.user)
    charList = "\n".join([character.name for character in user.characters])
    embed = discord.Embed(title="Characters", description=charList, color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

@tree.command(name = "view_current_character", description = "View your currently selected character", guild=discord.Object(GUILD))
async def view_current_character(interaction : discord.Interaction):
    user = getUser(interaction.user)
    embed = discord.Embed(title=user.currentCharacter.name, description="Mode: " + user.currentCharacter.mode.capitalize() + "\n" + user.currentCharacter.profile, color=discord.Color.blue())
    embed.set_thumbnail(url=user.currentCharacter.icon)
    await interaction.response.send_message(embed=embed)
    embed = discord.Embed(title="Properties", description="Temperature: " + str(user.currentCharacter.temperature) + "\n" + "Top_p: " + str(user.currentCharacter.top_p) + "\n" + "Top_k: " + str(user.currentCharacter.top_k) + "\n" + "Repetition Penalty: " + str(user.currentCharacter.repetition_penalty) + "\n" + "Max Length: " + str(user.currentCharacter.max_new_len), color=discord.Color.blue())
    await interaction.channel.send(embed=embed)
    convo = "\n".join(user.currentCharacter.conversation)
    embed = discord.Embed(title="Conversation History", description=convo, color=discord.Color.blue())
    await interaction.channel.send(embed=embed)

@tree.command(name = "help", description = "Help", guild=discord.Object(GUILD))
async def list_characters(interaction : discord.Interaction):
    user = getUser(interaction.user)
    charList = "\n".join([character.name for character in user.characters])
    embed = discord.Embed(title="List of Commands (Commands are self explanatory)", description=
"""Mention the bot to get a response

/create_character - create a character
/edit_properties - edit character properties
/edit_profile - edit character profile

/change_character - change character
/list_characters - list all characters
/view_current_character - view current character

/set_seed - set seed
/randomize_seed - randomize seed
/delete_character - delete a character

/change_mode - change interaction mode
/delete_last_interaction - delete the last interaction
/retry_last_interaction - retry the last interaction
/clear_memory - clear character memory

/character_suggestions - get suggestions for how to improve your character profile!

Be warned that if the bot is turned off for some reason all your character data will disappear, if you write any dedicated characters make sure to save them in a text file somewhere.
If the bot doesn't respond to a command or fails an interaction or doesn't update your character info, report it as a bug, if the bot simply takes a long time to reply to you or doesn't reply at all it probably isn't an issue related to the bot.
""", color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

@tree.command(name = "set_seed", description = "Set the seed of the character. ", guild=discord.Object(GUILD))
async def set_seed(interaction : discord.Interaction, new_seed : str):
    user = getUser(interaction.user)
    if new_seed.isdigit():
        new_seed = int(new_seed)
        user.currentCharacter.seed = new_seed
        await interaction.response.send_message("Changed seed to ```" + str(new_seed) + "```")
    else:
        await interaction.response.send_message("Invalid input")

@tree.command(name = "randomize_seed", description = "Randomize character seed", guild=discord.Object(GUILD))
async def randomize_seed(interaction : discord.Interaction):
    user = getUser(interaction.user)
    new_seed = random.randint(0, 1000000)
    user.currentCharacter.seed = new_seed
    await interaction.response.send_message("Changed seed to ```" + str(new_seed) + "```")

class edit_profile_modal(ui.Modal, title = "Edit Profile"):
    def __init__(self, targetChar):
        super().__init__()
        self.targetChar = targetChar
    description = ui.TextInput(label="Describe your character.", placeholder="Female? Male? Likes music? Relationship with the user?", default="CHARACTER is a ", required=True)
    responsetype = ui.TextInput(label="How do the character and user interact?", placeholder="Are they helpful, annoyed, and will they have censorship?", default="CHARACTER gives responses that are ", required=False)
    examples = ui.TextInput(label="Give some examples character responses.", placeholder="\"Tysm!! :) ^^\", \"Annoying, go away...\", etc", default="Some things CHARACTER might say include: ", required=False)
    misc = ui.TextInput(label="Anything else?", required=False)
    async def on_submit(self, interaction : discord.Interaction):
        newProfile = self.description.value + (" " if self.responsetype.value != "" else "") + self.responsetype.value + (" " if self.examples.value != "" else "") + self.examples.value + (" " if self.misc.value != "" else "") + self.misc.value
        self.targetChar.profile = newProfile
        await interaction.response.send_message("Changed character profile to ```" + newProfile + "```")

@tree.command(name = "edit_profile", description = "Edit your current character's profile. This gives it its personality.", guild=discord.Object(GUILD))
async def create_character(interaction : discord.Interaction):
    user = getUser(interaction.user)
    await interaction.response.send_modal(edit_profile_modal(user.currentCharacter))

# Bot receives mentions and responds to them using the current character with the AI
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    user = getUser(message.author)

    if client.user.mention in message.content.split():
        async with message.channel.typing():
            # Respond to the user message
            user.currentCharacter.lastQuestion = " ".join(message.content.split()[1:])
            response = await user.currentCharacter.request(" ".join(message.content.split()[1:]))
            # Split up response if it is longer than 2k chars
            if (len(response) > 2000):
                for i in range ((int(len(response)/2000)) + 1):
                    await sendCharacterMessage(message.channel, message.author.id, response[i*2000:i*2000+2000], user.currentCharacter)
            else:
                await sendCharacterMessage(message.channel, message.author.id, response, user.currentCharacter)

# Finishes setting up the bot
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(GUILD))
    guild = await client.fetch_guild(GUILD)
    for w in await guild.webhooks():
        await w.delete()
    print(f'Logged in to Discord as {client.user}')
client.run(TOKEN)