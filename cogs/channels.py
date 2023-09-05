import data
import model
import discord
from discord.ext import commands
from discord import app_commands

async def setup(bot : commands.Bot):
    await bot.add_cog(Channels(bot))

# Cog that allows the creation of character channels, where a character can be talked to by multiple users
class Channels(commands.Cog):
    bot : commands.Bot
    
    def __init__(self, bot : commands.Bot):
        self.bot = bot

    @app_commands.command(name = "create_channel", description = "Create a new character channel with your currently selected character.")
    async def create_channel(self, interaction : discord.Interaction):
        if isinstance(interaction.channel, discord.DMChannel):
            embed = discord.Embed(description="This cannot be done in DMs!", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            return
        
        user = data.get_user(interaction.user.id)
        c = model.Character(-1, user.currentCharacter.name, user.currentCharacter.icon, user.currentCharacter.model, memory=user.currentCharacter.memory,
                            temperature=user.currentCharacter.temperature, top_p = user.currentCharacter.top_p, top_k = user.currentCharacter.top_k, repetition_penalty = user.currentCharacter.repetition_penalty, max_new_len=user.currentCharacter.max_new_len)
        c.setProfile(user.currentCharacter.profile)
        c.systemPrompt = c.multiUserSystemPrompt

        if not interaction.guild in data.guildCat or not data.guildCat[interaction.guild] in interaction.guild.categories:
            data.guildCat[interaction.guild] = await interaction.guild.create_category(name="Character Channels")

        channel = CharacterChannel(await interaction.guild.create_text_channel(name=c.name, category=data.guildCat[interaction.guild], topic="PLEASE DO NOT USE SLASH COMMANDS HERE BESIDES \"/delete_channel\" THEY WILL NOT DO ANYTHING!"),
                                    interaction.user, c)
        data.channelChar[channel.channel] = channel
        await interaction.response.send_message("Done!")

    @app_commands.command(name = "delete_channel", description = "Delete a character channel (you can only do this to your character channels).")
    async def delete_channel(self, interaction : discord.Interaction):
        if not interaction.channel in data.channelChar:
            embed = discord.Embed(description="Channel not found!", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            return
        
        if not (interaction.user == data.channelChar[interaction.channel].owner or interaction.user in data.admins or await self.bot.is_owner(interaction.user)):
            embed = discord.Embed(description="You do not own this channel nor have permissions to delete it!", color=discord.Color.yellow())
            await interaction.response.send_message(embed=embed)
            return
        
        await data.channelChar.pop(interaction.channel).channel.delete()
        await interaction.response.send_message("Done!")

class CharacterChannel:
    channel : discord.TextChannel
    owner : discord.User
    character : model.Character

    def __init__(self, channel : discord.TextChannel, owner : discord.User, character : model.Character):
        self.channel = channel
        self.owner = owner
        self.character = character