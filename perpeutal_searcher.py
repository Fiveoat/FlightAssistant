import datetime
import pandas
from flights_assistant_x import FlightAssistantX
import smtplib


def get_env_variables():
    with open('secrets.txt', 'r') as file:
        return {x.split('=')[0]: x.split('=')[1].replace('\n', '') for x in file.readlines()}


class PerpetualSearcher:
    def __init__(self):
        self.assistant = FlightAssistantX()
        self.env = get_env_variables()

    def send_email(self, subject, message):
        con = smtplib.SMTP('smtp.gmail.com', 587)
        con.ehlo()
        con.starttls()
        con.login('fiveoat@gmail.com', self.env['EMAIL_PASSWORD'])
        con.sendmail('fiveoat@gmail.com', 'fiveoat@gmail.com', f'Subject: {subject} \n\n{message}')
        con.quit()

    @staticmethod
    def schedule_search(destination, ideal_price, source='SLC', trip_length=14):
        dataframe = pandas.read_csv('scheduled.csv')
        dataframe = dataframe.append(pandas.DataFrame([[source, destination, ideal_price, trip_length]],
                                                      columns=dataframe.columns))
        dataframe.to_csv('scheduled.csv', index=False)

    def run_scheduled_searches(self):
        dataframe = pandas.read_csv('scheduled.csv')
        for _, scheduled in dataframe.iterrows():
            print(self.run_search(scheduled['destination'], scheduled['ideal_price'], scheduled['source'],
                                  scheduled['trip_length']))

    def run_search(self, destination, ideal_price, source='SLC', trip_length=14, alert=True):
        start = (datetime.datetime.today() + datetime.timedelta(days=1))
        return_date = str(start + datetime.timedelta(days=trip_length)).split(" ")[0]
        try:
            quote = self.assistant.get_cheapest_flight(source, destination, str(start).split(" ")[0], return_date)[
                'price']
        except TypeError:
            return None
        if ideal_price > quote:
            if alert:
                self.send_email(f'Price Notification For {destination}',
                                f'{destination} : ${quote} : Set ${ideal_price}')
        return quote


if __name__ == '__main__':
    perpetual = PerpetualSearcher()
    perpetual.run_scheduled_searches()
    # perpetual.schedule_search('JFK', 250)
    # print(perpetual.run_search('LAX', 420))
