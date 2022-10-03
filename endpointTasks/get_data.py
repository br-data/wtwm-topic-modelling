from dataclasses import replace
import requests
from json import load, dumps
from os import path
from typing import List, Dict
from jq import compile


class GetData:
    def __init__(self):
        self.url = 'https://kommentare.mdr.de/api/v2/search/comments'
        with open(path.abspath('.') + '/.credentials/coral-talk-token.json') as json_file:
            self.coral_token = load(json_file)["token"]

    def coral_request(self, from_date: str = "2022-09-14 10:00:00", to_date: str = "2022-09-14 11:00:00", page: int = 1):
        '''requests data from Coral Talk API
        :param from_date: date from which to start the search. The format is "2022-09-14 10:00:00"
        :param to_date: date until which to search. The format is "2022-09-14 11:00:00"
        '''

        headers = {
        'Authorization': 'Bearer ' + self.coral_token,
        'Content-Type': 'application/json',
        }
        
        data = {"filter": {"must": [{"date_range": {"created_at": {"from": from_date,"to": to_date}}}]},"sort": "-created_at","size": 20,"page": page}
        response = requests.post('https://kommentare.mdr.de/api/v2/search/comments', headers=headers, data=dumps(data)).json()

        # print error message if response json contains error key
        if 'error' in response:
            print(response['error'])
            return None

        return response

    def get_nd_json(self, data: List[Dict]):
        '''returns data as new delimited json'''
        return compile(".[]").input(data).text()

    def save_data(self, file_name: str, data: List[Dict]):
        '''saves data into data/<file_name>.json'''
        with open(path.abspath('.') + '/data/' + file_name + '.json', 'w+') as json_file:
            json_file.write(self.get_nd_json(data))

    def get_mdr_data(self, from_date: str = "2022-09-14 10:00:00", to_date: str = "2022-09-14 11:00:00"):
        '''gets data from Coral Talk API and saves it into data/<from_date>_to_<to_date>.json. It returns the string <from_date>_to_<to_date> so it can be grabbed later on by a load_data API.
        :param from_date: date from which to start the search. The format is "2022-09-14 10:00:00"
        :param to_date: date until which to search. The format is "2022-09-14 11:00:00"
        '''
        page = 1
        response = self.coral_request(from_date, to_date, page)
        data = response['items']
        # iterate over all the pages while there there are pages with items ie with comments data
        while len(response['items']) > 0:
            page += 1
            response = self.coral_request(from_date, to_date, page)
            data.extend(response['items'])

        file_name = (from_date + '_to_' + to_date).replace(' ', '_').replace(':', '_')
        self.save_data(file_name, data)

        import pdb
        pdb.set_trace()

        return file_name
