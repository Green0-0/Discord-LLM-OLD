import discord
import requests
import model
from io import StringIO
import logging

# Should only be called once
def init(Log_stream : StringIO):  
    # Get token and guild from file
    global TOKEN

    with open("token.txt", "r") as f:
        TOKEN = f.read()

    # Store which webhooks each character uses
    global webhookChannels
    webhookChannels = {}
    
    # Store user data (characters, conversations, and some metadata)
    global users
    users = {}

    # Store extensions, that is command groups to be loaded into the bot
    global extensions
    extensions = ["cogs.management", "cogs.memory", "cogs.messaging", "cogs.characters", "cogs.generics", "cogs.channels"]
    global skip
    skip = []

    # Stores a list of admins who have permission to manage the bot
    global admins
    admins = []
    
    global log_stream
    log_stream = Log_stream

    global guildCat
    guildCat = {}

    global channelChar
    channelChar = {}

    global LLMModels
    LLMModels = []

# Gets a user by their id. If the userid isn't associated with any user, a new user is created.
def get_user(userid : int) -> model.User:
    global users
    if userid in users:
        return users[userid]
    else:
        newUser = model.User()
        users[userid] = newUser
        return newUser

# Gets a webhook to send model messages through. If none is found, then create a new one
# This should NOT be called in dms, it will break
async def get_webhook(channel : discord.TextChannel, character : model.Character) -> discord.Webhook:
    global webhookChannels
    if channel not in webhookChannels:
        webhookChannels[channel] = {}
    if character in webhookChannels[channel]:
        return webhookChannels[channel][character]
    else:
        logging.info(f"<Log> Generated new webhook for character \"{character.name}\" in channel \"{channel.name}\"")
        avatar = requests.get(character.icon).content
        # If there isn't enough space for the new webhook (discord has a webhook limit), delete one from the cache
        if len(webhookChannels[channel]) > 9:
            toDelete = webhookChannels[channel].popitem()
            logging.info(f"<Log> Deleted webhook \"{toDelete[1].name}\" to make space for new one.")
            await toDelete[1].delete()
        w = await channel.create_webhook(name=character.name, avatar=avatar)
        webhookChannels[channel][character] = w 
        return w
