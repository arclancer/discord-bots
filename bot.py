import os
from discord.ext import commands
from dotenv import load_dotenv
from utils.dota_matches import Scraper

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MAIN_PAGE = "https://liquipedia.net/dota2/Liquipedia:Upcoming_and_ongoing_matches"

bot = commands.Bot(command_prefix='!')

@bot.command(name='dota_matches',help='Retrieves upcoming DOTA 2 matches within the next 24 hours.')

async def on_message(ctx, text_parameter=None):

    match_scraper = Scraper()
    current_matches = match_scraper.scrape_matches(url=MAIN_PAGE)
    
    message = ""

    if text_parameter:
        current_matches = [match for match in current_matches if text_parameter.lower() in match.lower()]

    for match in current_matches:
        match = match + "\n-----------\n"
        if len(message + match) >= 2000:
            await ctx.send(message)
            message = ""
        message += match
    
    await ctx.send(message)

bot.run(TOKEN)