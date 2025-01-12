import datetime
import math
import pytz
import random
import requests


class BadResponse(Exception):
    pass


class Zone(object):
    def __init__(self, latitude: str, longitude: str, name: str | None = None, zone_id: str | None = None):
        self.latitude: str = latitude
        self.longitude: str = longitude
        self.name: str = name
        self.zone_id: str = zone_id
        if None in {name, zone_id}:
            self.name, self.zone_id = self.find_zone()

    def find_zone(self) -> (str, str):
        properties = call(self.url_zones())["features"][0]["properties"]
        return properties["name"], properties["id"]

    def url_zones(self) -> str:
        return f"https://api.weather.gov/zones?type=land&point={self.latitude},{self.longitude}&include_geometry=false"


class Place(object):
    def __init__(self, latitude: str, longitude: str, name: str | None = None, wfo: str | None = None,
                 x: str | None = None, y: str | None = None, forecast_zone: Zone = None):
        self.latitude: str = latitude
        self.longitude: str = longitude
        self.name: str = name
        self.wfo: str = wfo
        self.x: str = x
        self.y: str = y
        self.forecast_zone: Zone = forecast_zone
        if None in {name, wfo, x, y}:
            self.name, self.wfo, self.x, self.y = self.find_place()
        if forecast_zone is None:
            self.forecast_zone = Zone(latitude, longitude)

    def find_place(self) -> (str, str, str, str):
        properties = call(self.url_points())["properties"]
        return (f'{properties["relativeLocation"]["properties"]["city"]}, '
                f'{properties["relativeLocation"]["properties"]["state"]}',
                properties["gridId"], properties["gridX"], properties["gridY"])

    def url_points(self) -> str:
        return f"https://api.weather.gov/points/{self.latitude},{self.longitude}"

    def url_forecast(self) -> str:
        return f"https://api.weather.gov/gridpoints/{self.wfo}/{self.x},{self.y}/forecast"

    def url_hourly_forecast(self) -> str:
        return f"https://api.weather.gov/gridpoints/{self.wfo}/{self.x},{self.y}/forecast/hourly"

    def url_mapclick(self, unit: str = "1") -> str:  # si
        return (f"https://forecast.weather.gov/MapClick.php?lat={self.latitude}&lon={self.longitude}&unit={unit}&"
                f"lg=english&FcstType=json")

    def url_graphical(self, unit: str = "0") -> str:  # us
        return (f"https://forecast.weather.gov/MapClick.php?lat={self.latitude}&lon={self.longitude}&unit={unit}&"
                f"lg=english&FcstType=graphical")

    def get_forecast(self) -> dict:
        return call(self.url_forecast())

    def get_hourly_forecast(self) -> dict:
        return call(self.url_hourly_forecast())

    def get_mapclick(self) -> dict:
        return call(self.url_mapclick())

    def get_observation(self) -> dict:
        return self.get_mapclick()["currentobservation"]


def call(url: str) -> dict:
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise BadResponse(f"{response.status_code}")


def check_ok() -> bool:
    return call("https://api.weather.gov")["status"] == "OK"


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


def convert_speed(value: float, from_unit: str, to_unit: str) -> float:
    # height units: mps, mph

    conversion_table: dict = {
        ("mps", "mph"): 5280*(12*2.54/100)/3600,
        ("mph", "mps"): 3600*(100/(12*2.54))/5280
    }

    try:
        return value * conversion_table[(from_unit, to_unit)]
    except KeyError:
        raise ValueError(f"Unknown height conversion: {(from_unit, to_unit).__repr__()}")


def water_vapor_pressure(dry_bulb_temperature: float, relative_humidity: float) -> float:
    # C, % -> hPa
    return relative_humidity / 100 * 6.105 * math.exp((17.27 * dry_bulb_temperature) / (237 + dry_bulb_temperature))


def apparent_temperature(dry_bulb_temperature: float, relative_humidity: float, wind_speed: float) -> float:
    # C, %, mps
    e = water_vapor_pressure(dry_bulb_temperature, relative_humidity)
    return dry_bulb_temperature + 0.33 * e - 0.7 * wind_speed - 4


def fmt(value: float) -> str:
    return f"{math.floor(value * 100)}%"


test_place = Place("42.3555", "-71.0565")  # boston


def chance_of_snow_day(predicted_temperature: float, predicted_snowfall: float) -> float:
    dt: datetime.datetime = datetime.datetime.now(tz=pytz.timezone("EST"))

    # mathy math

    return random.random()


def main():
    print(fmt(chance_of_snow_day(266, 4)))


if __name__ == "__main__":
    print(check_ok())
    print(test_place.url_graphical())
    print(test_place.get_hourly_forecast())
    main()
