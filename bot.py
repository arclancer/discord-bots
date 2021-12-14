import os
from discord.ext import commands
from dotenv import load_dotenv
from utils.dota_matches import Scraper

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MAIN_PAGE = "https://liquipedia.net/dota2/Liquipedia:Upcoming_and_ongoing_matches"

bot = commands.Bot(command_prefix='!')

@bot.command(name='dota_matches',help='Retrieves upcoming DOTA 2 matches.')

async def on_message(ctx, text_parameter=None):

    match_scraper = Scraper()
    current_matches = match_scraper.scrape_matches(url=MAIN_PAGE)
    
    if text_parameter:
        filtered_match_list = [match for match in current_matches if text_parameter.lower() in match.lower()]
        match_list = "\n".join(filtered_match_list)
        
    else:
        match_list = "\n".join(current_matches)
    
    response = match_list
    await ctx.send(response)

bot.run(TOKEN)