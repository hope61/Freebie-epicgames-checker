# Import necessary libraries
import requests
import discord
from discord.ext import tasks, commands
import asyncio
import aiosqlite
import datetime
import dotenv
import sys
import os

# Import custom functions
from core.response import create_embed
from db import db_create, get_guild_ids, add_guild, get_channel_id

#TODO make error handlers so the bot doesnt die without u knowing where it died from

# Define the main function to run the bot
def run_bot():

    dotenv.load_dotenv()
    TOKEN = str(os.getenv("TOKEN"))
    
    # Define the Epic Games API URL
    epic_url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

    # Define the Discord client and command prefix
    intents = discord.Intents.default()
    intents.members = True
    bot = discord.Bot()

    # Define a list to keep track of the games that have already been sent
    sent_games = []

    # Define the function to get the list of free games from Epic Games API
    def get_free_games():
        # Send a GET request to the Epic Games API and return a list of free games
        response = requests.get(epic_url)
        data = response.json()
        free_games = []
        for game in data['data']['Catalog']['searchStore']['elements']:
            original_price = game['price']['totalPrice']['originalPrice']
            discount_price = game['price']['totalPrice']['discountPrice']
            if original_price != 0 and discount_price == 0:
                free_games.append(game)
        return free_games

    async def send_embed():
        # This function continuously sends an embedded message with free games to subscribed Discord channels
        while True:
            try:
                free_games = get_free_games()
                if free_games:
                    for game in free_games:
                        if game['title'] not in sent_games:
                            embed = create_embed(game)
                            guild_ids = await get_guild_ids() # Get a list of guild IDs that have a channel ID set in the database
                            for guild_id in guild_ids:
                                channel_id = await get_channel_id(guild_id) # Get the channel ID for the current guild
                                if channel_id: # Only send the message if the channel ID is not None
                                    channel = bot.get_channel(channel_id)
                                    await channel.send(embed=embed)
                            sent_games.append(game['title'])
                    await asyncio.sleep(3600)
            except Exception as e:
                print(f"Error in send_embed: {e}")

    async def check_guilds_in_db():
        try:
            # This function checks if the bot is a member of any new guilds and adds them to the database
            guild_ids_db = await get_guild_ids()
            guilds_bot = bot.guilds

            for guild_id in guilds_bot:
                if guild_id.id not in guild_ids_db:
                    await add_guild(guild_id)
                    #print(f"Added guild {guild_id.id} to the database.")
        except Exception as e:
                print(f"Error in check_guilds_in_db: {e}")

    async def clear_sent_games():
        # This function clears the sent_games list on the 1st day of every month
        while True:
            try:
                now = datetime.datetime.utcnow()
                if now.day == 1:
                    sent_games.clear()
                    print("Sent games list cleared.")
                await asyncio.sleep(86400)
            except Exception as e:
                    print(f"Error in clear_sent_games: {e}")

    @bot.event
    async def on_ready():
        # This function is called when the bot is ready to run
        print(f"{bot.user} is ready and online!")
        await db_create() # Create the database if it does not exist
        await check_guilds_in_db() # Check for new guilds and add them to the database
        bot.loop.create_task(clear_sent_games()) # Create a task to clear the sent_games list
        await send_embed() # Send the embedded message with free games
    
    @bot.event
    async def on_error(event, *args, **kwargs):
        # Log any errors that occur during bot events
        print(f"Error in {event}: {sys.exc_info()[0]}")

    # This function is called when the bot joins a new server (guild)
    # It takes the guild as a parameter and adds it to the database
    @bot.event
    async def on_guild_join(guild):
        guild_id = guild.id
        await add_guild(guild_id.id)

    # This command sets the channel where the bot will send free game notifications
    # It takes a TextChannel as a parameter and sets it as the announcement channel for the guild
    @bot.slash_command()
    async def set_channel(ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        channel_id = channel.id

        # Open a connection to the database
        async with aiosqlite.connect("main.db") as db:
            async with db.execute("SELECT * FROM main WHERE guild_id = ?", (guild_id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    # If there is no entry for this guild in the database, insert a new row with the guild and channel ids
                    await db.execute("INSERT INTO main(guild_id, channel_id) VALUES(?, ?)", (guild_id, channel_id))
                    await ctx.respond(f"Free game notifications will be sent to {bot.get_channel(channel_id).mention} on this server.")
                elif row[1] != channel_id:
                    # If the announcement channel has changed, update the row in the database with the new channel id
                    await db.execute("UPDATE main SET channel_id = ? WHERE guild_id = ?", (channel_id, guild_id))
                    await ctx.respond(f"Free game notifications will now be sent to {bot.get_channel(channel_id).mention} on this server.")
                else:
                    # If the channel is already set as the announcement channel, respond with a message indicating this
                    await ctx.respond("Free game notifications are already being sent to this channel on this server.")

            # Commit the changes to the database
            await db.commit()

    # This command sends the latest free games available on Epic Games
    @bot.slash_command()
    async def now(ctx):
        # Call the get_free_games function to retrieve the latest free games
        free_games = get_free_games()

        if free_games:
            # If there are free games, create an embed for each game and send them in separate messages
            for i, game in enumerate(free_games):
                embed = create_embed(game)
                if i == 0:
                    # If this is the first game in the list, respond with the embed
                    await ctx.respond(embed=embed)
                else:
                    # If this is not the first game in the list, send it in a new message
                    await ctx.send(embed=embed)
        else:
            # If there are no free games available, respond with a message indicating this
            await ctx.respond("No free games available at the moment.")

    # This command clears all data from the main table in the database
    @bot.slash_command()
    async def clear_db(ctx):
        # Check if the command is invoked by an admin
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("You don't have permission to use this command.")
            return

        # Open a connection to the database
        async with aiosqlite.connect('main.db') as db:
            # Execute the SQL command to delete all rows from the main table
            await db.execute("DELETE FROM main")

            # Commit the changes to the database
            await db.commit()

        # Respond with a message indicating that all data has been cleared
        await ctx.respond("All data in the main database has been cleared.")


    # Run the bot
    bot.run(TOKEN)