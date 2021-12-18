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
    
    def _match_ongoing_stream(self, team_one: str, team_two: str):

        """
        Matches the stream title to the teams that are currently playing the match.
        Ignores the Russian streams and returns the first non-Russian stream.
        """
        
        ongoing_streams = stream_requester.twitch_api_main('Dota 2')

        for stream in ongoing_streams:

            if re.search(rf"(?i)\b{team_one}\b", stream['stream_title']) and re.search(rf"(?i)\b{team_two}\b", stream['stream_title']):

                if not re.search(rf"(?i)\bRU\b", stream['stream_title']):

                    return stream['stream_name']
                
                else:
                    continue
            
            else:
                continue


    def _format_match_records(self, records: List[Dict]) -> List[str]:

        """
        Formats the list of matches to be displayed in Discord. Streams will be displayed if available.
        """
        
        match_list = []

        for match in records:

            if match['score'] != 'vs':

                stream_name = self._match_ongoing_stream(match['teams'][0], match['teams'][1])

                if stream_name:
                    match_as_string = f"{match['teams'][0]} vs {match['teams'][1]} | {match['Tournament']} | {match['match_format']} | Score: ||{match['score']}|| | ONGOING | <https://twitch.tv/{stream_name}>"
                
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
        Returns a HTML response from the URL with the list of matches.
        """

        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    
    def _parse_teams(self, response: requests.Response.text) -> Union[str, List, List]:

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

if __name__ == '__main__':

    match_scraper = ScrapeMatches()
    match_list = match_scraper.scrape_matches('https://liquipedia.net/dota2/Liquipedia:Upcoming_and_ongoing_matches')

    team_scraper = ScrapeTeams()
    message = team_scraper.scrape_teams('https://liquipedia.net/dota2/Fnatic')
    
    