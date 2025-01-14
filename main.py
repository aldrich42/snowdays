from functions import *
from scraper import *
from classes import *


def main():
    print(fmt(chance_of_snow_day(266, 4)))


if __name__ == "__main__":
    latlon = input(">>> ").split(",")
    test_place = Place(latlon[0], latlon[1])
    print(f"OK? {check_ok()}")
    main()


# todo: find out what the products mean
# todo: place all these places in one zone class
# todo sunrise/sunset
