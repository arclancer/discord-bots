import os
import re
from discord.ext import commands
from dotenv import load_dotenv
from utils.dota_script import ScrapeMatches, ScrapeTeams

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MAIN_PAGE = "https://liquipedia.net/dota2/"

bot = commands.Bot(command_prefix='!')

@bot.command(name='dota_matches',help='Retrieves upcoming DOTA 2 matches within the next 24 hours.')

async def on_message(ctx, *args):

    match_page = "Liquipedia:Upcoming_and_ongoing_matches"
    match_scraper = ScrapeMatches()
    current_matches = match_scraper.scrape_matches(url=MAIN_PAGE+match_page)
    
    message = ""

    if args:
        search_term = " ".join(args[:])
        current_matches = [match for match in current_matches if re.search(rf"\b{search_term.lower()}\b", match.lower())]

    for match in current_matches:
        match = match + "\n-----------\n"
        if len(message + match) >= 2000:
            await ctx.send(message)
            message = ""
        message += match
    
    await ctx.send(message)

@bot.command(name='dota_team', help='Retrieves members of the Dota team name given.')

async def on_message(ctx, *args):

    team_scraper = ScrapeTeams()
    team_name = "_".join(args[:])

    team_details = team_scraper.scrape_teams(url=MAIN_PAGE+team_name)
    message = "\n".join(team_details)

    await ctx.send(message)

bot.run(TOKEN)