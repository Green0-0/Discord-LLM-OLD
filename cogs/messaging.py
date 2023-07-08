import sys
import traceback
import data
import model

import discord
from discord.ext import commands
from discord import app_commands

async def setup(bot : commands.Bot):
    await bot.add_cog(Messaging(bot))

# Sends a message using webhooks (if possible) to roleplay as a defined character with custom avatar and name
async def send_message_as_character(userid : int, channel, message : str, character : model.Character):
    # Webhooks do not work in dm, so roleplay is not possible. Simply sends the message.
    if isinstance(channel, discord.DMChannel):
        if (len(message) > 1900):
            for i in range ((int(len(message)/1900)) + 1):
                if (i == 0):
                    await channel.send(character.name + ": " + message[i*1900:i*1900+1900])
                else:
                    await channel.send(message[i*1900:i*1900+1900])
        else:
            await channel.send(character.name + ": " + message)
        
    else: 
        # Tries to find a webhook from the cache, if not found uses a new one.
        webhook = await data.get_webhook(userid, channel, character)
        
        # Split up response if it is longer than 2k chars, then sends the message using the webhook previously retrieved
        if (len(message) > 1900):
            for i in range ((int(len(message)/1900)) + 1):
                await webhook.send(message[i*1900:i*1900+1900])
        else:
            await webhook.send(message)

# Cog that manages all events which require an LLM response
class Messaging(commands.Cog):
    bot : commands.Bot
    
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    # Bot receives mentions and responds to them using the current character with the AI
    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):
        if message.author == self.bot.user:
            return

        user = data.get_user(message.author.id)

        text = message.content.split()
        if self.bot.user.mention == text[0]:
            async with message.channel.typing():
                # Respond to the user message
                user.currentCharacter.lastQuestion = " ".join(text[1:])
                response = await user.currentCharacter.request(" ".join(text[1:]))
                await send_message_as_character(message.author.id, message.channel, response, user.currentCharacter)
        elif message.content.startswith("."):
            async with message.channel.typing():
                # Respond to the user message
                text = message.content[1:].strip()
                user.currentCharacter.lastQuestion = text
                response = await user.currentCharacter.request(text)
                await send_message_as_character(message.author.id, message.channel, response, user.currentCharacter)

    # Retries last interaction
    @app_commands.guilds(data.GUILD)
    @app_commands.command(name = "retry_last_interaction", description = "Retry the last interaction")
    async def retry_last_interaction(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)
        # Checks if the user has a stored question
        if user.currentCharacter.lastQuestion != "":
            # Make sure stored question matches conversation history, otherwise conversation character count might get messed up when undoing history
            if user.currentCharacter.conversation[-2] == f"USER: {user.currentCharacter.lastQuestion}":
                user.currentCharacter.currentConversationCharacters -= len(user.currentCharacter.conversation.pop()) + len(user.currentCharacter.conversation.pop())
                await interaction.response.defer()
                async with interaction.channel.typing():
                    # Respond to the user message
                    response = await user.currentCharacter.request(user.currentCharacter.lastQuestion)
                    await send_message_as_character(interaction.user.id, interaction.channel, response, user.currentCharacter)
            else:
                embed = discord.Embed(description="Unable to find last interaction.", color=discord.Color.yellow())
                await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(description="No interaction found.", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)

    # Suggestion model character used to generate suggestions
    SuggestionModel = model.Character(-1, "no memory", "Airoboros", "https://cdn.discordapp.com/embed/avatars/0.png", model.Airoboros65b, 0, 1.7, 0.95, 50, 1.2, 4000)
    # Get character profile suggestions using AI
    @app_commands.guilds(data.GUILD)
    @app_commands.command(name = "get_character_suggestions", description = "Get suggestions for your character's profile!")
    async def get_character_suggestions(self, interaction : discord.Interaction):
        user = data.get_user(interaction.user.id)

        await interaction.response.defer()
        async with interaction.channel.typing():
            # Respond to the user message
            response = await self.SuggestionModel.request(f"I am trying to write a character named \"{user.currentCharacter.name}\". Currently, I have their profile described as such: \"{user.currentCharacter.profile.replace('CHARACTER', user.currentCharacter.name)}\". How can I improve upon this profile? How can I make it more interesting, unique, and complete in terms of personality? How can I improve the range and quality of interactions this character might have with someone else? Please also provide some examples of things this character might say. Make sure to answer all the questions above with an in depth description/response.")
            await send_message_as_character(interaction.user.id, interaction.channel, response, self.SuggestionModel)
                
