import os
import re
from discord.ext import commands
from dotenv import load_dotenv
from dota_script import ScrapeMatches, ScrapeTeams, ScrapeTournaments

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
        if not current_matches:
            message = f"No matches found for '{search_term}'. Try refining your search!"

    for match in current_matches:
        match = match + "\n-----------\n"
        if len(message + match) >= 2000:
            await ctx.send(message)
            message = ""
        message += match
    
    if not message:
        message = f"Looks like there aren't any upcoming matches in the next 24 hours. Check again later!"
    
    await ctx.send(message)

@bot.command(name='dota_team', help='Retrieves members of the Dota team name given.')

async def on_message(ctx, *args):

    team_scraper = ScrapeTeams()
    team_name = "_".join(args[:])

    try:

        team_details = team_scraper.scrape_teams(url=MAIN_PAGE+team_name)

        message = "\n".join(team_details)
    
    except TypeError:

        message = f"Looks like a page for {team_name} does not exist yet, or the team name is spelt incorrectly. Please try again."
    
    except IndexError:

        message = f"{team_name} currently has an incomplete roster, or is inactive. Visit the team profile page here: {MAIN_PAGE+team_name}"

    await ctx.send(message)

@bot.command(name='dota_tournaments', help='Retrieves ongoing Dota 2 tournaments.')

async def on_message(ctx):

    tournament_scraper = ScrapeTournaments()

    tournament_details = tournament_scraper.scrape_tournaments(MAIN_PAGE)

    message = "\n-----------\n".join(tournament_details)

    await ctx.send(message)

bot.run(TOKEN)