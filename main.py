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
            Location(Point("42.3555,-71.0565"),
                     grid_data=GridPoint("Boston", "MA", "BOX", "72", "90", "KBOX"),
                     zone=Zone("MAZ025", "Suffolk"),
                     station=Station("KBOS", "Boston, Logan International Airport")),  # boston
        )
        print("accessed locations")
        print(fmt(chance_of_snow_day(test_district)))


if __name__ == "__main__":
    main()


# todo: good product names: AFM, FZL, HYD, LCO, RR9
# todo sunrise/sunset
# todo use rr9 for
# todo scrape power company's website
