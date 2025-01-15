import random
from api_functions import check_ok
from scraper import *
from functions import *
from classes import *
import datetime


def chance_of_snow_day(area: District) -> float:
    dt: datetime.datetime = datetime.datetime.now()

    # mathy math

    return random.random()


def fmt(value: float) -> str:
    return f"{math.floor(value * 100)}%"


def main():
    if check_ok():
        test_district: District = District(
            Location(Point("40.7128,-74.0060")),  # new york
            Location(Point("34.0549,-118.2426")),  # los angeles
            Location(Point("41.8781,-87.6298")),  # chicago
            Location(Point("29.7601,-95.3701")),  # houston
            Location(Point("33.4484,-112.0740")),  # phoenix
            Location(Point("39.9526,-75.1652")),  # philadelphia
        )
        print("accessed locations")
        print(fmt(chance_of_snow_day(test_district)))


if __name__ == "__main__":
    main()


# todo: good product names: AFM, FZL, HYD, LCO, RR9
# todo sunrise/sunset
# todo use rr9 for
# todo scrape power company's website
