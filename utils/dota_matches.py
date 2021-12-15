import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
from datetime import datetime, timedelta

class Scraper:

    def __init__(self):
        self.time_upper_bound = datetime.now() + timedelta(hours=16)

    def _request_matches(self, url: str) -> requests.Response.text:

        """
        Returns a HTML response from the URL with the list of matches.
        """

        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    
    def _parse(self, response: requests.Response.text) -> List[Dict]:

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

            for tag in score_details:
                match_details['score'] = tag.text[:-6]
                
            for tag in match_format:
                if 'Bo' in tag.text:
                    match_details['match_format'] = tag.text
            
            for tag in all_teams:

                if 'data-highlightingclass' in tag.attrs.keys():
                    team = tag['data-highlightingclass']
                    teams.append(team)

                if 'data-timestamp' in tag.attrs.keys():

                    match_datetime = datetime.strptime(tag.text, '%B %d, %Y - %H:%M %Z')
                    
                    match_details['time'] = tag.text
                    match_details['datetime'] = match_datetime
                
                if 'data-stream-twitch' in tag.attrs.keys():

                    if tag['data-stream-twitch'] == 'Beyond_the_Summit':
                        tag['data-stream-twitch'] = tag['data-stream-twitch'].replace('_','').lower()

                    if tag['data-stream-twitch'] == 'ESL_Dota_2':
                        tag['data-stream-twitch'] = 'ESL_DOTA2'

                    match_details['stream_name'] = tag['data-stream-twitch'] 
                    
                match_details['teams'] = teams

            for tag in tournament_details:
                
                if 'title' in tag.attrs.keys():
                    tag_count += 1
                    if tag_count % 7 == 0:
                        match_details['Tournament'] = tag['title']

            if match_details in all_matches:
                continue
            
            all_matches.append(match_details)

        return all_matches
    
    def _filter_records(self, records: List[Dict]) -> List[Dict]:

        """
        Records are filtered; matches without a scoreline have been played, and so will be ignored.
        Matches past the upper bound (24 hours in the future) will also be filtered to prevent bloat.
        """

        filtered_records = [record for record in records if record['score'] and record['datetime'] < self.time_upper_bound]
        return filtered_records

    def _format_records(self, records: List[Dict]) -> List[str]:

        """
        Formats the list of matches to be displayed in Discord.
        """

        match_list = []

        for match in records:

            if match['score'] != 'vs':
                match_as_string = f"{match['teams'][0]} vs {match['teams'][1]} | {match['Tournament']} | {match['match_format']} | Score: ||{match['score']}|| | ONGOING | <https://twitch.tv/{match['stream_name']}>"
            
            else:
                match_as_string = f"{match['teams'][0]} vs {match['teams'][1]} | {match['Tournament']} | {match['match_format']} | {datetime.strftime(match['datetime'] + timedelta(hours=8), '%B %d, %Y - %I:%M %p')} | <https://twitch.tv/{match['stream_name']}>"
    
            match_list.append(match_as_string)
        
        return match_list

    def scrape_matches(self, url: str) -> List[Dict]:

        """
        The main function to call the other private functions.
        """

        response = self._request_matches(url)
        all_matches = self._parse(response)
        filtered_matches = self._filter_records(all_matches)
        current_match_list = self._format_records(filtered_matches)

        return current_match_list

if __name__ == '__main__':

    scraper = Scraper()
    match_list = scraper.scrape_matches('https://liquipedia.net/dota2/Liquipedia:Upcoming_and_ongoing_matches')
