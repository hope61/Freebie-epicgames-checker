# Freebie-EpicGames-Checker Discord Bot

This Discord bot checks for new free games in Epic Games and sends notifications to subscribed channels.

## Getting Started

To use this bot, you will need to do the following:

1. Clone the repository to your local machine.
2. Install the required Python libraries using pip: `pip install -r requirements.txt`
3. Create a new Discord bot and get the bot token.
4. Create a new file called `.env` in the project root directory and add the following line to it: `TOKEN=<your_bot_token>`
5. Run the bot: `python main.py`

## Features

- Sends an embedded message with the details of new free games in Epic Games.
- Automatically sends notifications to subscribed channels when new free games become available.
- Allows users to subscribe to notifications by setting a channel where the bot will send free game notifications.

## Commands

- `/set_channel` - This sets the notification channel
- `/now` - This shows the current free games
