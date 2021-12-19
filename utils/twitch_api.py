import requests
import os
import time
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

class RequestStreams:

    def __init__(self):
        
        self.twitch_request_url_base = 'https://api.twitch.tv/helix/'
        self.request_headers = {
            'Authorization': '',
            'Client-Id': TWITCH_CLIENT_ID
        }
        

    def _request_access_token(self, client_id: str, client_secret: str):

        token_url = f'https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'

        try:
            response = requests.post(token_url)

            if response.status_code == 200:
                jsonResponse = response.json()
                
                self.request_headers['Authorization'] = 'Bearer' + ' ' + jsonResponse['access_token']
            
            else:
                print(f'Error: Status Code {response.status_code} encountered.')
        
        except Exception as e:
            print(f'Operation failed due to {e}')
    
    def _request_game_id(self, game_title: str) -> str:

        game_id_endpoint = self.twitch_request_url_base + f'games?name={game_title}'
        
        try:
            response = requests.get(game_id_endpoint, headers=self.request_headers)

            if response.status_code == 200:
            
                game_id = response.json()['data'][0]['id']

                return game_id
            
            else:
                print(f'Error: Status Code {response.status_code} encountered.')
        
        except Exception as e:
            print(f'Operation failed due to {e}')

    def _request_stream_titles(self, game_id: str) -> List[Dict]:

        stream_titles_endpoint = self.twitch_request_url_base + f'streams?game_id={game_id}'

        try:

            response = requests.get(stream_titles_endpoint, headers=self.request_headers)
            
            if response.status_code == 200:
                streams = response.json()['data']

                return streams
            
            else:
                print(f'Error: Status Code {response.status_code} encountered.')
        
        except Exception as e:
            print(f'Operation failed due to {e}')
    
    def _format_streams(self, all_streams: List[Dict]) -> List[Dict]:

        formatted_streams = []
        stream_dict = {}

        for stream in all_streams:
            stream_dict['channel_name'] = stream['user_name']
            stream_dict['stream_language'] = stream['language']
            stream_dict['stream_title'] = stream['title']
            formatted_streams.append(stream_dict)
            stream_dict = {}
        
        return formatted_streams

    def twitch_api_main(self, game_title: str) -> List[Dict]:
        
        self._request_access_token(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
        game_id = self._request_game_id(game_title)
        all_streams = self._request_stream_titles(game_id)
        formatted_streams = self._format_streams(all_streams)
        
        return formatted_streams


if __name__ == '__main__':

    requester = RequestStreams()
    requester.twitch_api_main('Dota 2')