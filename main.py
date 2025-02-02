import math
import numpy as np
import requests
import random
import datetime


nws_headers = None


class BadResponse(Exception):
    pass


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


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
    return call_json("https://api.weather.gov")["status"] == "OK"


def nws_duration_to_int(nws_duration: str) -> int:
    values = nws_duration.split("T")
    if values[0] == "P":
        return int(values[1][:-1])
    else:
        return int(values[0][1:-1]) * 24 + int(values[1][:-1])


def nws_str_to_datetime(nws_str: str) -> datetime.datetime:
    return datetime.datetime(int(nws_str[:4]), int(nws_str[5:7]), int(nws_str[8:10]),
                             int(nws_str[11:13]), int(nws_str[14:16]), int(nws_str[17:19]))


def nws_str_to_datetime_with_duration(nws_str: str) -> (datetime.datetime, int):
    duration = nws_duration_to_int(nws_str[26:])
    return datetime.datetime(int(nws_str[:4]), int(nws_str[5:7]), int(nws_str[8:10]),
                             int(nws_str[11:13]), int(nws_str[14:16]), int(nws_str[17:19])), duration


def nws_dict_to_datetime_dict(json_data: dict, method: int = 0) -> dict:
    out: dict = {}
    for value in json_data["values"]:
        dt, dur = nws_str_to_datetime_with_duration(value["validTime"])
        if method == 0:
            for i in range(dur):
                if value["value"] == "null":
                    v = 0.0
                else:
                    v = float(value["value"])
        elif method == 1:
            for i in range(dur):
                if value["value"] == "null":
                    v = 0.0
                else:
                    v = float(value["value"])
                out[dt + datetime.timedelta(hours=i)] = v / dur
        else:
            raise ValueError(f"unknown method: {method.__repr__()}")
    return out


class Forecast(object):
    def __init__(self, json_data: dict):  # make it all numpy?
        self.temp = nws_dict_to_datetime_dict(json_data["properties"]["temperature"])
        self.dew = nws_dict_to_datetime_dict(json_data["properties"]["dewpoint"])
        self.rh = nws_dict_to_datetime_dict(json_data["properties"]["relativeHumidity"])
        self.at = nws_dict_to_datetime_dict(json_data["properties"]["apparentTemperature"])
        self.wind_chill = nws_dict_to_datetime_dict(json_data["properties"]["windChill"])
        self.wind_direction = nws_dict_to_datetime_dict(json_data["properties"]["windDirection"])
        self.wind_speed = nws_dict_to_datetime_dict(json_data["properties"]["windSpeed"])
        self.prop = nws_dict_to_datetime_dict(json_data["properties"]["probabilityOfPrecipitation"])
        self.quop = nws_dict_to_datetime_dict(json_data["properties"]["quantitativePrecipitation"], method=1)
        self.ice = nws_dict_to_datetime_dict(json_data["properties"]["iceAccumulation"], method=1)
        self.snowfall = nws_dict_to_datetime_dict(json_data["properties"]["snowfallAmount"], method=1)


class FZL(object):
    def __init__(self, str_data):
        self.i = str_data


class LCO(object):
    def __init__(self, str_data):
        self.i = str_data


class RR9(object):
    def __init__(self, str_data):
        self.i = str_data


class Observations(object):
    def __init__(self, json_data: dict):
        properties = json_data["features"][0]["properties"]
        print(properties)
        self.timestamp: datetime = nws_str_to_datetime(properties["timestamp"])
        self.temp = properties["temperature"]["value"]
        self.dew = properties["dewpoint"]["value"]
        self.rh = properties["relativeHumidity"]["value"]
        # self.at = properties["apparentTemperature"]["value"]
        self.wind_chill = properties["windChill"]["value"]
        self.wind_direction = properties["windDirection"]["value"]
        self.wind_speed = properties["windSpeed"]["value"]
        # self.prop = properties["probabilityOfPrecipitation"]["value"]
        # self.quop = properties["quantitativePrecipitation"]["value"]
        # self.ice = properties["iceAccumulation"]["value"]  # all these are prev precip
        # self.snowfall = properties["snowfallAmount"]["value"]

class Alert(object):  # keep?
    pass


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

    def get_sunrise(self):
        pass


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

    def get_product(self, product_code: str):
        url = f"https://api.weather.gov/products?office={self.radar}&type={product_code}&limit=1"
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

    def get_fzl(self):
        return FZL(self.grid_data.get_product("FZL"))

    def get_lco(self):
        return LCO(self.grid_data.get_product("LCO"))

    def get_rr9(self):
        return RR9(self.grid_data.get_product("RR9"))

    def get_observations(self):
        return Observations(self.station.get_observations_json())


class District(object):
    def __init__(self, center: Location, *margin: Location):
        self.center: Location = center
        self.margin: tuple[Location, ...] = margin


def convert():
    pass

def neural_net():
    pass

def snowday_score():
    pass


def fmt(value: float) -> str:
    return f"{math.floor(sigmoid(value) * 100)}%"


def main():
    if check_ok():
        test_district: District = District(
            Location(Point("42.3555,-71.0565"),
                     # grid_data=GridPoint("Boston", "MA", "BOX", "72", "90", "KBOX"),
                     # zone=Zone("MAZ025", "Suffolk"),
                     # station=Station("KBOS", "Boston, Logan International Airport")
                     )
        )
        print(test_district.center.get_rr9().i)


if __name__ == "__main__":
    main()


# todo: good product names: HYD, RR9
# todo scrape power company's website
