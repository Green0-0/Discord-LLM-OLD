# Discord-LLM
Runs a LLM using the API from https://www.neuroengine.ai/. 
This is my best attempt at making a comprehensive UI for LLMs on a discord bot, similar to those found in popular webUIs. The main feature in this bot is the creation of characters, which contains a profile that is injected into the bot's system prompt. Dropdowns and modals are used to make the bot user-friendly and sleek. Other commands are also present, like the option to remember conversations, configure LLM parameters (temperature, top_p, etc). Characters send messages through webhooks, which contain an avatar and name for the character, so the bot can pretend to be different users during roleplay. There is also the ability to turn a character into a conversation thread, where multiple users can talk to one character in a unique discord channel. In this thread, a user can also ask another character they have made to respond to the character in the thread.

To run the bot, simply download the code and paste the token for a bot in the token file. Then give your bot manage channel and manage webhook permissions, and let the bot run. Use the command /reload every time the bot is turned on, or when the code is updated, to sync the bot to its latest update (you do not need to restart the bot to perform updates, except for those modifying data.py, model.py, or bot.py). Be warned that restarting the bot will result in loss of user data. To alleviate this, all commands will dump the character profile whenever it is created/edited so it can be found through discord's message search feature, unless the message or channel is manually deleted. Additionally, after restarting the bot it is recommended to use /purge_webhooks to make sure there isn't leftovers from the previous bot instance.

To use the bot, either use /help to get a list of commands (the commands are self explanatory), or ping the bot to talk.

Examples of basic functionality:

![image](https://github.com/Green0-0/Discord-LLM/assets/138409197/ea23e408-5fa5-4827-bb55-c330709491a1)
![image](https://github.com/Green0-0/Discord-LLM/assets/138409197/23a824a9-5647-4f78-9a6f-09c83de6f72c)

Example character thread (Note: The AI's beliefs are not reflective of my own):

![image](https://github.com/Green0-0/Discord-LLM/assets/138409197/8ee22300-2ad0-4472-bdfa-59d2766f8cf9)
![image](https://github.com/Green0-0/Discord-LLM/assets/138409197/e70b82d6-ce39-49d5-a9c8-5ca388f5990b)
![image](https://github.com/Green0-0/Discord-LLM/assets/138409197/cf7de5db-2956-4be6-85be-8bbcce7a4bed)


Example of character creation:

![charactercreation](https://github.com/Green0-0/Discord-LLM/assets/138409197/1d3b5134-06c5-49e6-9ab6-5d0524f51b05)

Warning:
Editing the system prompt as this bot does will significantly decrease both alignment and truthfulness. The content generated may be wrong, toxic, biased, or harmful. As with any LLM, nothing AI generated should be taken seriously, at least without significant fact checking. You, and you alone are liable for the outputs the AI models generate.
