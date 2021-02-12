from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Flights(Base):
    __tablename__ = 'flights'
    flight_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    source = Column(String)
    destination = Column(String)
    ideal_price = Column(Integer)
    trip_length = Column(String)
    departure_date = Column(String)
    return_date = Column(String)


class DatabaseHandler:
    def __init__(self):
        self.engine = create_engine('sqlite:///data.sqlite')
        self.session = sessionmaker(bind=self.engine)()

    def _create_database(self):
        Base.metadata.create_all(bind=self.engine)

    def query(self, sql_statement):
        return [x for x in self.engine.execute(sql_statement)]

    def commit(self, sql_statement):
        try:
            self.engine.execute(sql_statement)
            self.session.commit()
            return True
        except Exception:
            return False

    def insert(self, flight):
        self.session.add(flight)
        self.session.commit()

    def delete(self, flight):
        self.session.delete(flight)
        self.session.commit()

    def get_all_scheduled(self, destination=None):
        if destination is None:
            return [x for x in self.session.query(Flights)]
        return [x for x in self.session.query(Flights).filter_by(destination=destination)]

    def get_flight(self, destination, source, ideal_price, departure_date, return_date):
        return [x for x in self.session.query(Flights).filter_by(destination=destination, source=source,
                                                                 ideal_price=ideal_price, departure_date=departure_date,
                                                                 return_date=return_date)][0]


if __name__ == '__main__':
    database = DatabaseHandler()
