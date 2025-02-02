import math
import numpy as np
import requests
import random
import datetime


nws_headers = None


class BadResponse(Exception):
    pass


def call(url: str, headers: dict | None) -> requests.Response:
    response = requests.get(url, headers=headers)
    print(f"GET: {url} ({response.status_code})")
    if response.status_code == 200:
        return response
    else:
        raise BadResponse(f"{response.status_code}")


def call_json(url: str, headers: dict | None = None) -> dict:
    return call(url, headers).json()


def call_html(url: str, headers: dict | None = None) -> NotImplemented:
    return NotImplemented


def check_ok() -> bool:
    return call_json("https://api.weather.gov/")["status"] == "OK"


def nws_str_to_datetime(nws_str: str) -> datetime.datetime:
    print(nws_str[11:13])
    return datetime.datetime(int(nws_str[:4]), int(nws_str[5:7]), int(nws_str[8:10]),
                             int(nws_str[11:13]), int(nws_str[14:16]), int(nws_str[17:19]))


def nws_dict_to_datetime_dict(json_data: dict) -> dict:
    out: dict = {}
    for value in json_data["values"]:
        out[nws_str_to_datetime(value["validTime"])] = value["value"]
    return out


class Forecast(object):
    def __init__(self, json_data: dict):
        self.temperature = nws_dict_to_datetime_dict(json_data["properties"]["temperature"])


class Point(object):
    def __init__(self, latlon_str: str):
        self.latitude: str
        self.longitude: str
        self.latitude, self.longitude = tuple(latlon_str.split(","))

    def get_grid_data(self):
        url = f"https://api.weather.gov/points/{self.latitude},{self.longitude}"
        data = call_json(url, headers=nws_headers)["properties"]
        return GridPoint(data["relativeLocation"]["properties"]["city"],
                         data["relativeLocation"]["properties"]["state"],
                         data["gridId"], data["gridX"], data["gridY"], data["radarStation"])

    def get_zone(self):
        url = f"https://api.weather.gov/zones?type=land&point={self.latitude},{self.longitude}&include_geometry=false"
        data = call_json(url, headers=nws_headers)["features"][0]["properties"]
        return Zone(data["id"], data["name"])


class GridPoint(object):
    def __init__(self, mun: str, state: str, wfo: str, grid_x: str, grid_y: str, radar: str):
        self.mun: str = mun
        self.state: str = state
        self.wfo: str = wfo
        self.grid_x: str = grid_x
        self.grid_y: str = grid_y
        self.radar: str = radar

    def get_station(self):
        url = f"https://api.weather.gov/gridpoints/{self.wfo}/{self.grid_x},{self.grid_y}/stations"
        data = call_json(url, headers=nws_headers)["features"][0]["properties"]
        return Station(data["stationIdentifier"], data["name"])

    def get_forecast_json(self):
        url = f"https://api.weather.gov/gridpoints/{self.wfo}/{self.grid_x},{self.grid_y}"
        return call_json(url, headers=nws_headers)

    def get_headlines_json(self):
        url = f"https://api.weather.gov/offices/{self.wfo}/headlines"
        return call_json(url, headers=nws_headers)

    def get_rr9_chart(self):
        url = f"https://api.weather.gov/products?office={self.radar}&type=RR9&limit=1"
        url2 = call_json(url, headers=nws_headers)["@graph"][0]["@id"]
        return call_json(url2, headers=nws_headers)["productText"]


class Zone(object):
    def __init__(self, zone_id: str, name: str):
        self.id: str = zone_id
        self.name: str = name

    def get_alerts_json(self):
        url = f"https://api.weather.gov/alerts?zone={self.id}"
        return call_json(url, headers=nws_headers)


class Station(object):
    def __init__(self, station_id: str, name: str):
        self.id: str = station_id
        self.name: str = name

    def get_observations_json(self):
        url = f"https://api.weather.gov/stations/{self.id}/observations"
        return call_json(url, headers=nws_headers)


class Location(object):
    def __init__(self, latlon: Point, grid_data: GridPoint | None = None, zone: Zone | None = None,
                 station: Station | None = None):
        self.latlon: Point = latlon
        self.grid_data: GridPoint
        self.zone: Zone
        self.station: Station
        if grid_data is None:
            self.grid_data = self.latlon.get_grid_data()
        else:
            self.grid_data = grid_data
        if zone is None:
            self.zone = self.latlon.get_zone()
        else:
            self.zone = zone
        if station is None:
            self.station = self.grid_data.get_station()
        else:
            self.station = station

    def get_forecast(self):
        return Forecast(self.grid_data.get_forecast_json())


class District(object):
    def __init__(self, center: Location, *margin: Location):
        self.center: Location = center
        self.margin: tuple[Location, ...] = margin

def convert_temp(value: float, from_unit: str, to_unit: str) -> float:
    # temp units: C, F

    def c_to_f(c: float) -> float:
        return c * 9/5 + 32

    def f_to_c(f: float) -> float:
        return (f - 32) * 5/9

    conversion_table: dict = {
        ("C", "F"): c_to_f, ("F", "C"): f_to_c,
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


def calculate_sunrise():
    pass


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
        # print(fmt(chance_of_snow_day(test_district)))
        print(list(test_district.center.get_forecast().temperature.keys())[0])


if __name__ == "__main__":
    main()


# todo: good product names: AFM, FZL, HYD, LCO, RR9
# todo sunrise/sunset
# todo use rr9 for
# todo scrape power company's website
