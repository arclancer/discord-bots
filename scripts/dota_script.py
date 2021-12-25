import requests
from bs4 import BeautifulSoup
import re
import time
from utils.twitch_api import RequestStreams
from typing import List, Dict, Union
from datetime import datetime, timedelta

stream_requester = RequestStreams()

class ScrapeMatches:

    def __init__(self):
        self.time_upper_bound = datetime.now() + timedelta(hours=16)
        self.blacklisted_words = ['Gaming', 'Team', 'e-sports', 'Esports', 'esports']

    def _request_matches(self, url: str) -> requests.Response.text:

        """
        Returns a HTML response from the URL with the list of matches.
        """

        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    
    def _parse_matches(self, response: requests.Response.text) -> List[Dict]:

        """
        Parses the HTML response from the GET request.
        """

        all_matches = []

        soup = BeautifulSoup(response, 'html.parser')

        surface_level_elements = soup.find_all('tbody')

        for tags in surface_level_elements:
            
            match_details = {}
            teams = []
            tag_count = 0

            score_details = tags.find_all('td', attrs={'class':'versus'})
            all_teams = tags.find_all('span')
            match_format = tags.find_all('abbr')
            tournament_details = tags.find_all('a')

            for tag in all_teams:

                if 'data-highlightingclass' in tag.attrs.keys():

                    team = tag['data-highlightingclass']
                    teams.append(team)

                if 'data-timestamp' in tag.attrs.keys():

                    match_datetime = datetime.strptime(tag.text, '%B %d, %Y - %H:%M %Z')
                    
                    match_details['time'] = tag.text
                    match_details['datetime'] = match_datetime
                    
                match_details['teams'] = teams

            for tag in score_details:
                match_details['score'] = tag.text[:-6]
                
            for tag in match_format:
                if 'Bo' in tag.text:
                    match_details['match_format'] = tag.text

            for tag in tournament_details:
                
                if 'title' in tag.attrs.keys():
                    tag_count += 1
                    if tag_count % 7 == 0:
                        match_details['Tournament'] = tag['title']

            if len(match_details.keys()) == 6:

                if match_details in all_matches or 'TBD' in match_details['teams']:
                    continue
                    
                else:
                    all_matches.append(match_details)

        return all_matches
    
    def _filter_records(self, records: List[Dict]) -> List[Dict]:

        """
        Records are filtered; matches without a scoreline have been played, and so will be ignored.
        Matches past the upper bound (24 hours in the future) will also be filtered to prevent bloat.
        """

        filtered_records = [record for record in records if record['score'] and record['datetime'] < self.time_upper_bound]
        return filtered_records
    
    def _get_team_keywords(self, team_one: str, team_two: str) -> Union[List[str], List[str]]:

        """
        Often, team names include common naming conventions e.g. Nemiga [Gaming], Gambit [Esports], Vici [Gaming]
        It is very common in matches to use alternative names of competitive teams, such as their initials, or without the naming convention.
        The goal here is to retrieve alternative keywords of the team name.
        For example, Nemiga Gaming could yield ['Nemiga Gaming', 'Nemiga', 'NG'].
        This is to improve the logic in the regex matching for stream names.
        """

        team_one_keywords = [team_one]
        team_two_keywords = [team_two]
        
        for team in [team_one, team_two]:
            if re.search(r"[\(].*?[\)]", team):
                processed_team = re.sub(r"[\(].*?[\)]", "", team).strip()
                if team == team_one:
                    team_one_keywords.append(processed_team)
                    team_one = processed_team
                else:
                    team_two_keywords.append(processed_team)
                    team_two = processed_team
        
        for word in self.blacklisted_words:
            for team in [team_one, team_two]:
                if word in team:
                    modified_keyword = team.replace(word, '').strip()
                    if modified_keyword in team_one:
                        team_one_keywords.append(modified_keyword)
                    else:
                        team_two_keywords.append(modified_keyword)
        
        team_one_split = team_one.split()
        team_two_split = team_two.split()

        for split_team in [team_one_split, team_two_split]:
            if len(split_team) > 1:
                abbreviation = ''.join([letter[0] for letter in split_team])
                if split_team == team_one_split:
                    team_one_keywords.append(abbreviation)
                    team_one_keywords.append(abbreviation.upper())
                else:
                    team_two_keywords.append(abbreviation)
                    team_two_keywords.append(abbreviation.upper())

        return team_one_keywords, team_two_keywords            

    def _match_ongoing_stream(self, team_one_keywords: List[str], team_two_keywords: List[str]) -> Dict:

        """
        Matches the stream title to the teams that are currently playing the match.
        Returns the English-speaking stream with the most views; if no English-speaking streams are found,
        the first non-English-speaking stream will be returned instead.
        """
        
        english_streams = []
        other_streams = []
        ongoing_streams = stream_requester.twitch_api_main('Dota 2')

        team_one_keywords = '|'.join(team_one_keywords)
        team_two_keywords = '|'.join(team_two_keywords)

        for stream in ongoing_streams:

            if re.search(rf"(?i)\b{team_one_keywords}\b", stream['stream_title']) or re.search(rf"(?i)\b{team_two_keywords}\b", stream['stream_title']):
                if stream['stream_language'] == 'en':
                    english_streams.append(stream)
                else:
                    other_streams.append(stream)
        
        if english_streams:
            return english_streams[0]
        
        elif other_streams:
            return other_streams[0]
        
    def _format_match_records(self, records: List[Dict]) -> List[str]:

        """
        Formats the list of matches to be displayed in Discord. Streams will be displayed if available.
        """
        
        match_list = []

        for match in records:

            if match['score'] != 'vs':

                team_one_keywords, team_two_keywords = self._get_team_keywords(match['teams'][0], match['teams'][1])
                stream_name = self._match_ongoing_stream(team_one_keywords, team_two_keywords)

                if stream_name:
                    match_as_string = f"{match['teams'][0]} vs {match['teams'][1]} | {match['Tournament']} | {match['match_format']} | Score: ||{match['score']}|| | ONGOING | <https://twitch.tv/{stream_name['channel_name']}> [{stream_name['stream_language'].upper()}]"
                
                else:
                    match_as_string = f"{match['teams'][0]} vs {match['teams'][1]} | {match['Tournament']} | {match['match_format']} | Score: ||{match['score']}|| | ONGOING"
            else:
                match_as_string = f"{match['teams'][0]} vs {match['teams'][1]} | {match['Tournament']} | {match['match_format']} | {datetime.strftime(match['datetime'] + timedelta(hours=8), '%B %d, %Y - %I:%M %p')}"
    
            match_list.append(match_as_string)
        
        return match_list

    def scrape_matches(self, url: str) -> List[str]:

        """
        The main function to call the other private functions.
        """

        response = self._request_matches(url)
        all_matches = self._parse_matches(response)
        filtered_matches = self._filter_records(all_matches)
        current_match_list = self._format_match_records(filtered_matches)

        return current_match_list

class ScrapeTeams:

    def __init__(self):
        pass

    def _request_teams(self, url: str) -> requests.Response.text:

        """
        Returns a HTML response from the URL with the list of teams.
        """

        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    
    def _parse_teams(self, response: requests.Response.text) -> Union[str, List, List]:

        """
        Parses the HTML response and returns the roster details for each team.
        """

        soup = BeautifulSoup(response,'html.parser')

        team_name = soup.find('span', attrs={'dir':'auto'}).text
        active_roster = soup.find('div', attrs={'class': 'roster table-responsive'})

        for tag in active_roster:
            
            players = tag.find_all('span', attrs={'id':'player'})
            join_dates = tag.find_all('div', attrs={'class':'Date'})

            roster = [player.text for player in players]
            roster_join_dates = sorted([join_date.text[:10] for join_date in join_dates if re.match(r"^[\d-]+$", join_date.text[:10])], reverse=True)

        latest_join_date = roster_join_dates[0]

        return team_name, roster, latest_join_date
        
    def _format_message(self, team_name: str, roster: List, latest_join_date: str) -> List[str]:

        """
        Formats the Discord message that the bot will send.
        """

        team_formation_date = datetime.strptime(latest_join_date, '%Y-%m-%d').strftime('%d %B %Y')

        discord_message = [f'**{team_name}**, as of {team_formation_date}']

        for i in range(0, 5):

            player_details = f"Position {i+1}: {roster[i]}"

            discord_message.append(player_details)
        
        return discord_message
    
    def scrape_teams(self, url: str) -> List[str]:

        response = self._request_teams(url)
        team_name, roster, latest_join_date = self._parse_teams(response)
        message = self._format_message(team_name, roster, latest_join_date)

        return message

class ScrapeTournaments:

    def __init__(self):
        self.all_tournaments = []

    def _request_tournaments(self, url: str) -> requests.Response.text:

        """
        Returns a HTML response from the URL with the list of teams.
        """

        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    
    def _parse_tournaments(self, response: requests.Response.text):

        """
        Parses the HTML response and returns all ongoing tournaments' details.
        """
        
        soup = BeautifulSoup(response, 'html.parser')
        all_tournament_lists = soup.find_all('ul', attrs={'class': 'tournaments-list'})

        for tournaments in all_tournament_lists:
            
            tournaments_classified = tournaments.find_all('li')

            for tournament_list in tournaments_classified:
                tournament_list_tags = tournament_list.find_all('span', attrs={'class': 'tournaments-list-heading'})
                for tags in tournament_list_tags:
                    if tags.text == 'Ongoing':
                        ongoing_tournaments = tournament_list.find_all('ul', attrs={'class':'tournaments-list-type-list'})
        
        for tournament in ongoing_tournaments:

            for tags in tournament:
                
                tournament_details = {}
                tournament_page_links = tags.find('a')
                tournament_names = tags.find('span', attrs={'class':'tournaments-list-name'})
                tournament_dates = tags.find('small', attrs={'class':'tournaments-list-dates'})
                tournament_details['link'] = tournament_page_links['href']
            
                tournament_details['name'] = tournament_names.text
            
                tournament_details['date'] = tournament_dates.text

                self.all_tournaments.append(tournament_details)
    
    def _format_message(self, tournaments: List[Dict]) -> List[str]:

        """
        Formats the Discord message to be sent by the bot.
        """

        discord_message = ["**Ongoing Tournaments**"]

        for tournament in tournaments:

            details = f"**{tournament['name']}**   |   {tournament['date']}   |   <https://liquipedia.net{tournament['link']}>"
            discord_message.append(details)
        
        return discord_message
    
    def scrape_tournaments(self, url: str) -> List[str]:

        response = self._request_tournaments(url)
        self._parse_tournaments(response)
        message = self._format_message(self.all_tournaments)

        return message

if __name__ == '__main__':

    match_scraper = ScrapeMatches()
    match_list = match_scraper.scrape_matches('https://liquipedia.net/dota2/Liquipedia:Upcoming_and_ongoing_matches')

    team_scraper = ScrapeTeams()
    message = team_scraper.scrape_teams('https://liquipedia.net/dota2/Fnatic')

    tournament_scraper = ScrapeTournaments()
    all_tourneys = tournament_scraper.scrape_tournaments('https://liquipedia.net/dota2/Main_Page')
    