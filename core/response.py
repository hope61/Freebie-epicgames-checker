import discord
from datetime import datetime, timedelta

def create_embed(game):
    embed = discord.Embed(title=game['title'], url=f"https://www.epicgames.com/store/en-US/p/{game['productSlug']}", description=game['description'], color=0x7c00ff)
    embed.set_thumbnail(url=game['keyImages'][0]['url'])
    embed.add_field(name="💰 Original Price", value=f"~~${game['price']['totalPrice']['originalPrice'] / 100}~~", inline=False)
    embed.add_field(name="💸 Discount Price", value="Free", inline=False)
    
    # Calculate the expiration date and add it as a field
    expiration_date_str = game['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['endDate']
    expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    days_left = (expiration_date - datetime.utcnow()).days
    expiration_string = expiration_date.strftime('%B %d, %Y at %I:%M %p UTC')
    embed.add_field(name="🕒 Expires On", value=f"{expiration_string} ({days_left} days left)", inline=False)

    # Add a footer with a note about the expiration date
    embed.set_footer(text="Note: The expiration date is in UTC timezone.")
    
    return embed
