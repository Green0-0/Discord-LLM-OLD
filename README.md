# Discord-LLM
Runs a LLM using the API from https://www.neuroengine.ai/. 
This is my best attempt at making a comprehensive UI for LLMs on a discord bot, similar to those found in popular webUIs. The main feature in this bot is the creation of characters, which contains a profile that is injected into the bot's system prompt. Dropdowns and modals are used to make the bot user-friendly and sleek. Other commands are also present, like the option to remember conversations, configure LLM parameters (temperature, top_p, etc). Characters send messages through webhooks, which contain an avatar and name for the character, so the bot can pretend to be different users during roleplay. There is also the ability to turn a character into a conversation thread, where multiple users can talk to one character in a unique discord channel. In this thread, a user can also ask another character they have made to respond to the character in the thread.

To run the bot, simply download the code and paste the token for a bot in the token file. Then give your bot manage channel and manage webhook permissions, and let the bot run. Use the command /reload every time the bot is turned on, or when the code is updated, to sync the bot to its latest update (you do not need to restart the bot to perform updates, except for those modifying data.py, model.py, or bot.py). Be warned that restarting the bot will result in loss of user data. To alleviate this, all commands will dump the character profile whenever it is created/edited so it can be found through discord's message search feature, unless the message or channel is manually deleted. Additionally, after restarting the bot it is recommended to use /purge_webhooks to make sure there isn't leftovers from the previous bot instance.

To use the bot, either use /help to get a list of commands (the commands are self explanatory), or ping the bot to talk.

Example character thread (Note: The AI's beliefs are not reflective of my own)

![multiagent](https://github.com/Green0-0/Discord-LLM/assets/138409197/60d439bf-51fd-4d79-8bd6-c44e7fe0ee89)


Example creating characters

![charactercreation](https://github.com/Green0-0/Discord-LLM/assets/138409197/1d3b5134-06c5-49e6-9ab6-5d0524f51b05)


Note: The bot is unstable as the latest update with character threads changed a lot of the code, more testing is needed.
