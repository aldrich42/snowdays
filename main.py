import random
from api_functions import check_ok
from scraper import *
from functions import *
from classes import *
import datetime
import pytz


def chance_of_snow_day(predicted_temperature: float, predicted_snowfall: float) -> float:
    dt: datetime.datetime = datetime.datetime.now(tz=pytz.timezone("EST"))

    # mathy math

    return random.random()


def fmt(value: float) -> str:
    return f"{math.floor(value * 100)}%"


def main():
    latlon = input(">>> ").split(",")
    if check_ok():
        test_place = Place(latlon[0], latlon[1])
        print(fmt(chance_of_snow_day(266, 4)))


if __name__ == "__main__":
    main()


# todo: find out what the products mean
# todo: place all these places in one zone class
# todo sunrise/sunset
