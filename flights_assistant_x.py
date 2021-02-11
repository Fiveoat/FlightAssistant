import requests
from currency_converter import CurrencyConverter
import pandas


def get_env_variables():
    with open('secrets.txt', 'r') as file:
        return {x.split('=')[0]: x.split('=')[1].replace('\n', '') for x in file.readlines()}


class FlightAssistantX:
    def __init__(self):
        self.env = get_env_variables()
        self.base_url = 'https://test.api.amadeus.com/'
        self.token = self.get_token()

    def get_token(self):
        return requests.post("https://test.api.amadeus.com/v1/security/oauth2/token",
                             headers={"Content-Type": "application/x-www-form-urlencoded"},
                             data={'grant_type': 'client_credentials', 'client_id': self.env['AMADEUS_ID'],
                                   'client_secret': self.env['AMADEUS_SECRET']}).json()['access_token']

    @staticmethod
    def get_airports(country, size='large'):
        airports = pandas.read_csv('airports.csv')
        airports = airports[airports['type'] == size + '_airport']
        airports = airports[airports['iso_country'] == country]
        if country == 'US':
            return [x.lstrip("K") for x in airports['code'].tolist()]
        return airports['code'].tolist()

    def get_quotes(self, source, destination, date, return_date, num_passengers=1, max_results=5):
        url = self.base_url
        url += 'v2/shopping/flight-offers?'
        url += 'originLocationCode=' + source
        url += '&destinationLocationCode=' + destination
        url += '&departureDate=' + date
        url += '&returnDate=' + return_date
        url += f'&adults={num_passengers}'
        url += f'&max={max_results}'
        try:
            return requests.get(url, headers={'Authorization': f'Bearer {self.token}'}).json()['data']
        except KeyError:
            return None

    def get_flight_data(self, source, destination, date, return_date, num_passengers=1, max_results=5):
        flights = []
        converter = CurrencyConverter()
        data = self.get_quotes(source, destination, date, return_date, num_passengers=num_passengers,
                               max_results=max_results)
        if data is None:
            return None
        for quote in data:
            flights.append({'source': source, 'destination': destination,
                            'price': round(converter.convert(quote['price']['base'], 'EUR', 'USD'), 2),
                            'carrier': quote['validatingAirlineCodes'][0]})
        return pandas.DataFrame(flights).sort_values('price')

    def get_cheapest_flight(self, source, destination, date, return_date, num_passengers=1, max_results=5):
        data = self.get_flight_data(source, destination, date, return_date, num_passengers=num_passengers,
                                    max_results=max_results)
        try:
            return data[data['price'] == data["price"].min()].iloc[0]
        except TypeError:
            return None


if __name__ == '__main__':
    assistant = FlightAssistantX()
    print(assistant.get_flight_data('SLC', 'JFK', '2021-02-19', '2021-04-20', max_results=200, num_passengers=2))
