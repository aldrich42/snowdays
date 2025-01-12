import datetime
import math
import pytz
import random
import requests


URL_PREFIX = "https://api.weather.gov"


class BadResponse(ValueError):
    pass


class Place(object):
    def __init__(self, name: str, wfo: str, x: int, y: int):
        self.name: str = name
        self.wfo: str = wfo
        self.x: int = x
        self.y: int = y

    def get_forecast(self):
        return call(f"{URL_PREFIX}/gridpoints/{self.wfo}/{self.x},{self.y}/forecast")

    def get_hourly_forecast(self):
        return call(f"{URL_PREFIX}/gridpoints/{self.wfo}/{self.x},{self.y}/forecast/hourly")


def find_place(latitude: str, longitude: str) -> Place:
    properties = call(f"https://api.weather.gov/points/{latitude},{longitude}")["properties"]
    return Place(f'{properties["relativeLocation"]["properties"]["city"]}, '
                 f'{properties["relativeLocation"]["properties"]["city"]}',
                 properties["gridId"], properties["gridX"], properties["gridY"])


def check_ok() -> bool:
    response = requests.get(URL_PREFIX)
    if response.status_code == 200:
        return response.json()["status"] == "OK"
    else:
        raise BadResponse(f"{response.status_code}")


def call(url: str) -> dict:
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise BadResponse(f"{response.status_code}")


def convert_temp(value: float, from_unit: str, to_unit: str) -> float:
    # temp units: K, C, F

    def k_to_c(k: float) -> float:
        return k - 273.15

    def k_to_f(k: float) -> float:
        return (k - 273.15) * 9/5 + 32

    def c_to_k(c: float) -> float:
        return c + 273.15

    def c_to_f(c: float) -> float:
        return c * 9/5 + 32

    def f_to_k(f: float) -> float:
        return (f - 32) * 5/9 + 273.15

    def f_to_c(f: float) -> float:
        return (f - 32) * 5/9

    conversion_table: dict = {
        ("K", "C"): k_to_c, ("K", "F"): k_to_f,
        ("C", "K"): c_to_k, ("C", "F"): c_to_f,
        ("F", "K"): f_to_k, ("F", "C"): f_to_c,
    }

    try:
        return conversion_table[(from_unit, to_unit)](value)
    except KeyError:
        raise ValueError(f"Unknown temperature conversion: {(from_unit, to_unit).__repr__()}")


def convert_height(value: float, from_unit: str, to_unit: str) -> float:
    # height units: cm, m, in, ft

    conversion_table: dict = {
        ("cm", "m"): 1/100, ("cm", "in"): 1/2.54, ("cm", "ft"): 1/(2.54*12),
        ("m", "cm"): 100, ("m", "in"): 100/2.54, ("m", "ft"): 100/(12*2.54),
        ("in", "cm"): 2.54, ("in", "m"): 2.54/100, ("in", "ft"): 1/12,
        ("ft", "cm"): 12*2.54, ("ft", "m"): 12*2.54/100, ("ft", "in"): 12
    }

    try:
        return value * conversion_table[(from_unit, to_unit)]
    except KeyError:
        raise ValueError(f"Unknown height conversion: {(from_unit, to_unit).__repr__()}")


def fmt(value: float) -> str:
    return f"{math.floor(value * 100)}%"


places: dict[str: Place] = {
    "test_place": find_place("42.3555", "-71.0565")
}


def chance_of_snow_day(predicted_temperature: float, predicted_snowfall: float) -> float:
    dt: datetime.datetime = datetime.datetime.now(tz=pytz.timezone("EST"))

    # mathy math

    return random.random()


def main():
    print(fmt(chance_of_snow_day(266, 4)))


if __name__ == "__main__":
    print(check_ok())
    print(places["test_place"].get_hourly_forecast())
    main()
