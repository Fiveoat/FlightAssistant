from flights_assistant_x import FlightAssistantX
from schema import DatabaseHandler, Flights
import datetime
import smtplib


def get_env_variables():
    with open('secrets.txt', 'r') as file:
        return {x.split('=')[0]: x.split('=')[1].replace('\n', '') for x in file.readlines()}


class PerpetualSearcher:
    def __init__(self):
        self.assistant = FlightAssistantX()
        self.database_handler = DatabaseHandler()
        self.env = get_env_variables()

    def remove_scheduled(self, destination, ideal_price, departure_date, return_date, source):
        flight = self.database_handler.get_flight(destination, source, ideal_price, departure_date, return_date)
        self.database_handler.delete(flight)

    @staticmethod
    def depart_day_passed(departure_date):
        if datetime.datetime.today() > datetime.datetime.strptime(departure_date, "%Y-%m-%d"):
            return True
        return False

    def send_email(self, subject, message):
        con = smtplib.SMTP('smtp.gmail.com', 587)
        con.ehlo()
        con.starttls()
        con.login('fiveoat@gmail.com', self.env['EMAIL_PASSWORD'])
        con.sendmail('fiveoat@gmail.com', 'fiveoat@gmail.com', f'Subject: {subject} \n\n{message}')
        con.quit()

    def determine_dates(self, departure_date, return_date, trip_length):
        if departure_date is None:
            departure_date = (datetime.datetime.today() + datetime.timedelta(days=1))
        elif departure_date is False:
            return False, False
        else:
            if self.depart_day_passed(departure_date):
                return False, False
            departure_date = datetime.datetime.strptime(departure_date, "%Y-%m-%d")
        if return_date is None:
            return_date = str(departure_date + datetime.timedelta(days=trip_length)).split(" ")[0]
        departure_date = str(departure_date).split(" ")[0]
        return departure_date, return_date

    def schedule_search(self, destination, ideal_price, departure_date=None, return_date=None, source='SLC',
                        trip_length=14):
        departure_date, return_date = self.determine_dates(departure_date, return_date, trip_length)
        flight = Flights()
        flight.departure_date = departure_date
        flight.return_date = return_date
        flight.source = source
        flight.destination = destination
        flight.ideal_price = ideal_price
        flight.trip_length = trip_length
        self.database_handler.insert(flight)

    def run_search(self, destination, ideal_price, departure_date=None, return_date=None, source='SLC',
                   trip_length=14, alert=True):
        departure_date, return_date = self.determine_dates(departure_date, return_date, trip_length)
        if departure_date is False:
            self.remove_scheduled(destination, ideal_price, departure_date, return_date, source)
            return None
        try:
            data = self.assistant.get_cheapest_flight(source, destination, departure_date, return_date)
            quote = data['price']
        except (TypeError, KeyError):
            return None
        if ideal_price > quote:
            if alert:
                self.send_email(f'Price Notification For {destination}',
                                f'Price : ${quote} : Limit ${ideal_price} : '
                                f'Depart {departure_date} : Return {return_date} : With {data["carrier"]}')
        return quote

    def run_scheduled_searches(self):
        for flight in self.database_handler.get_all_scheduled():
            print(self.run_search(flight.destination, flight.ideal_price, flight.departure_date, flight.return_date,
                                  flight.source, flight.trip_length), flight.destination)


if __name__ == '__main__':
    perpetual = PerpetualSearcher()
    # x = ['LCY', 'GVA', 'CDG', 'OSL', 'HND', 'CTS', 'KEF']
    # for y in x:
    #     perpetual.schedule_search(y, 500, '2021-07-12')
    perpetual.run_scheduled_searches()
    # perpetual.schedule_search('YVR', 250, '2021-09-12')
    # perpetual.schedule_search('DEN', 250, '2021-09-12')
    # perpetual.schedule_search('PDX', 80, '2021-09-12')
    # print(perpetual.run_search('LAX', 420))
