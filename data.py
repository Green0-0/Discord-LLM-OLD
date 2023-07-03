import discord
import requests
import model
import pickle 

# Should only be called once
def init():  
    # Get token and guild from file
    global TOKEN
    global GUILD

    with open("token.txt", "r") as f:
        TOKEN = f.read()
    with open("guild.txt", "r") as f:
        GUILD = int(f.read())

    # Store webhooks so that new ones don't have to be constantly generated
    global webhooks
    webhooks = {}
    
    # Store user data (characters, conversations, and some metadata)
    global users
    users = {}

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
async def get_webhook(userid : int, textChannel : discord.TextChannel, character : model.Character) -> discord.Webhook:
    global webhooks
    key = f"{userid} {textChannel.id} {character.id}"
    if key in webhooks:
        print(f"<Log> Used cached webhook for character named {character.name} with id {character.id}")
        return webhooks[key]
    else:
        print(f"<Log> Generated new webhook for character named {character.name} with id {character.id}")
        avatar = requests.get(character.icon).content
        # If there isn't enough space for the new webhook (discord has a webhook limit), delete one from the cache
        if len(webhooks) > 9:
            print("<Log> Deleted webhook to make space for new one.")
            await webhooks.pop(0).delete()
        webhook = await textChannel.create_webhook(name=character.name, avatar=avatar)
        
        webhooks[key] = webhook 
        return webhook

