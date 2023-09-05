# Discord-LLM
Runs a LLM using the API from https://www.neuroengine.ai/. 
This is my best attempt at making a comprehensive UI for LLMs on a discord bot, similar to those found in popular webUIs. The main feature in this bot is the creation of characters, which contains a profile that is injected into the bot's system prompt. Dropdowns and modals are used to make the bot user-friendly and sleek. Other commands are also present, like the option to remember conversations, configure LLM parameters (temperature, top_p, etc). Characters send messages through webhooks, which contain an avatar and name for the character, so the bot can pretend to be different users during roleplay. There is also the ability to turn a character into a conversation channel, where multiple users can talk to one character in a unique discord channel. If you do not trust your server members, or are running a big server, it might be best to disable this by adding "cogs.channels" to the "skip" list in "data.py".

To run the bot, simply download the code and paste the token for a bot in the token file. Then give your bot manage channel and manage webhook permissions, and let the bot run. Use the command /reload every time the bot is turned on, or when the code is updated, to sync the bot to its latest update (you do not need to restart the bot to perform updates, except for those modifying data.py, model.py, or bot.py). Be warned that restarting the bot will result in loss of user data. To alleviate this, all commands will dump the character profile whenever it is created/edited so it can be found through discord's message search feature, unless the message or channel is manually deleted. Additionally, after restarting the bot it is recommended to use /purge_webhooks to make sure there isn't leftovers from the previous bot instance.

To use the bot, either use /help to get a list of commands (the commands are self explanatory), or ping the bot to talk.



Note: The bot is unstable after the latest update, more testing is needed.
Changes:
- Reworked the way messages are parsed. The name of a user is now injected in the format "user (username):" and messages are sliced when "user (xxx):" is detected OR when "character_name:" is detected.
- Multi user conversation channels were added. Heavily experimental, may not work
- Bot can now be updated while running
- Debug/repair commands
- Quick_create_character to make a character without modals
- Changed edit_properties to config, may tabulate the modal in a future update to add more options
- Removed the need for a guild text file, now the bot should theoretically work when added to multiple guilds
- Auxilary improvements
