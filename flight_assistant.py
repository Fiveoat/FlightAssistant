import requests
import datetime
import json
import pandas as pd
from time import sleep
from pprint import pprint


def get_env_variables():
    with open('secrets.txt', 'r') as file:
        return {x.split('=')[0]: x.split('=')[1].replace('\n', '') for x in file.readlines()}


class FlightAssistant:
    def __init__(self):
        self.env = get_env_variables()
        self.root_url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
        self.session = requests.Session()
        self.session.headers.update({'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
                                     'x-rapidapi-key': self.env['SKY_SCANNER_API']})

    def get_quote(self, source, destination, date):
        result = {}
        url = f"{self.root_url}/apiservices/browsequotes/v1.0/US/USD/en-US/{source}/{destination}/{date}"
        try:
            data = self.session.get(url).json()
            result['date'] = data['Quotes'][0]['OutboundLeg']['DepartureDate'].split("T")[0]
            result['carrier'] = data['Carriers'][0]['Name']
            result['source'] = data['Places'][0]['Name']
            result['destination'] = data['Places'][1]['Name']
            result['cost'] = data['Quotes'][0]['MinPrice']
            return result
        except IndexError or KeyError:
            return None


if __name__ == '__main__':
    assistant = FlightAssistant()
    date_range = pd.date_range('2021-08-12', '2021-12-07')
    count = 0
    for date in date_range:
        if count < 100:
            sleep(3)
            date = str(date).split(" ")[0]
            xi = assistant.get_quote('SLC', 'HNL', date)
            if xi is not None:
                print(xi)
            else:
                print("Nope", date)
                count += 1
