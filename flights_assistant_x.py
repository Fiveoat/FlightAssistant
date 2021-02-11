import requests
from currency_converter import CurrencyConverter
from pprint import pprint
import pandas


def get_env_variables():
    with open('secrets.txt', 'r') as file:
        return {x.split('=')[0]: x.split('=')[1].replace('\n', '') for x in file.readlines()}


class FlightAssistantX:
    def __init__(self):
        self.env = get_env_variables()
        self.token = self.get_token()
        self.base_url = 'https://test.api.amadeus.com/'

    def get_token(self):
        return requests.post("https://test.api.amadeus.com/v1/security/oauth2/token",
                             headers={"Content-Type": "application/x-www-form-urlencoded"},
                             data={'grant_type': 'client_credentials', 'client_id': self.env['AMADEUS_ID'],
                                   'client_secret': self.env['AMADEUS_SECRET']}).json()['access_token']

    def get_quotes(self, source, destination, date, return_date, num_passengers=1, max_results=5):
        self.base_url += 'v2/shopping/flight-offers?'
        self.base_url += 'originLocationCode=' + source
        self.base_url += '&destinationLocationCode=' + destination
        self.base_url += '&departureDate=' + date
        self.base_url += '&returnDate=' + return_date
        self.base_url += f'&adults={num_passengers}'
        self.base_url += f'&max={max_results}'
        return requests.get(self.base_url, headers={'Authorization': f'Bearer {self.token}'}).json()['data']

    def get_flight_data(self, source, destination, date, return_date, num_passengers=1, max_results=5):
        flights = []
        converter = CurrencyConverter()
        for quote in self.get_quotes(source, destination, date, return_date, num_passengers=num_passengers,
                                     max_results=max_results):
            flights.append({'source': source, 'destination': destination,
                            'price': converter.convert(quote['price']['base'], 'EUR', 'USD'),
                            'carrier': quote['validatingAirlineCodes'][0]})
        return pandas.DataFrame(flights).sort_values('price')

    def get_cheapest_flight(self, source, destination, date, return_date, num_passengers=1, max_results=5):
        data = self.get_flight_data(source, destination, date, return_date, num_passengers=num_passengers,
                                    max_results=max_results)
        return data[data['price'] == data["price"].min()].iloc[0]


if __name__ == '__main__':
    assistant = FlightAssistantX()
    print(assistant.get_cheapest_flight('SLC', 'JFK', '2021-02-19', '2021-04-20', max_results=200, num_passengers=2))
