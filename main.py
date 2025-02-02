from math import exp, floor
from time import time
import numpy as np
import requests
import datetime


nws_headers = None
sample_locations = input("points? ").split(";")


class BadResponse(Exception):
    pass


def sigmoid_normal(x):
    return 1 / (1 + exp(-x))


def rational_normal(x):
    return 1 - 1 / (1 + x)


def australian_at(temp_c: float, rh: float, wind_speed_kph):
    wind_speed_mps = wind_speed_kph / 3.6
    vapor_pressure = rh * 6.105 * exp((17.27 * temp_c) / (237.7 + temp_c))
    return temp_c + 0.33 * vapor_pressure - 0.7 * wind_speed_mps - 4


def count_calls(func):
    def wrapper(*args, **kwargs):
        wrapper.num_calls += 1
        return func(*args, **kwargs)
    wrapper.num_calls = 0
    return wrapper


@count_calls
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
                out[dt + datetime.timedelta(hours=i)] = v / dur
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


class Forecast(object):  # todo trim
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


class LCO(object):  # todo make real
    def __init__(self, str_data):
        self.i = str_data  #.split("\n")[27]


class Observations(object):
    def __init__(self, json_data: dict):
        properties = json_data["features"][0]["properties"]
        self.timestamp: datetime = nws_str_to_datetime(properties["timestamp"])
        self.temp = float(properties["temperature"]["value"])
        self.dew = float(properties["dewpoint"]["value"])
        self.rh = float(properties["relativeHumidity"]["value"])
        # self.wind_chill = float(properties["windChill"]["value"])
        self.wind_direction = float(properties["windDirection"]["value"])
        self.wind_speed = float(properties["windSpeed"]["value"])
        # self.precipitation_1h = float(properties["precipitationLastHour"]["value"])
        # self.precipitation_3h = float(properties["precipitationLast3Hours"]["value"])
        # self.precipitation_6h = float(properties["precipitationLast6Hours"]["value"])
        self.at = australian_at(self.temp, self.rh, self.wind_speed)

class Alert(object):  # keep?
    pass


class Point(object):
    def __init__(self, latlon_str: str):
        self.latitude: str
        self.longitude: str
        self.latitude, self.longitude = tuple(latlon_str.split(","))

    def __repr__(self):
        return f"Point('{self.latitude},{self.longitude}')"

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

    def __repr__(self):
        return (f"GridPoint({self.mun.__repr__()}, '{self.state}', '{self.wfo}', '{self.grid_x}', '{self.grid_y}', "
                f"'{self.radar}')")

    def get_station(self):
        url = f"https://api.weather.gov/gridpoints/{self.wfo}/{self.grid_x},{self.grid_y}/stations"
        data = call_json(url, headers=nws_headers)["features"][0]
        coordinates = data["geometry"]["coordinates"]
        point = f"{coordinates[1]:.4f},{coordinates[0]:.4f}"
        return Station(Point(point), data["properties"]["stationIdentifier"], data["properties"]["name"])

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

    def __repr__(self):
        return f"Zone('{self.id}', {self.name.__repr__()})"

    def get_alerts_json(self):
        url = f"https://api.weather.gov/alerts?zone={self.id}"
        return call_json(url, headers=nws_headers)


class Station(object):
    def __init__(self, latlon: Point, station_id: str, name: str):
        self.latlon: Point = latlon
        self.id: str = station_id
        self.name: str = name

    def __repr__(self):
        return f"Station({self.latlon.__repr__()}, '{self.id}', {self.name.__repr__()})"

    def get_observations_json(self):
        url = f"https://api.weather.gov/stations/{self.id}/observations"
        return call_json(url, headers=nws_headers)

    def get_observations(self):
        return Observations(self.get_observations_json())


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

    def __repr__(self):
        return f"Location({self.latlon.__repr__()}, grid_data={self.grid_data.__repr__()})"

    def __str__(self):
        return (f"{self.grid_data.mun}, {self.grid_data.state} ({self.latlon.latitude}, {self.latlon.longitude}): "
                f"{self.grid_data.wfo} {self.grid_data.grid_x}, {self.grid_data.grid_y}")

    def get_forecast(self):
        return Forecast(self.grid_data.get_forecast_json())

    def get_fzl(self):
        return FZL(self.grid_data.get_product("FZL"))

    def get_lco(self):
        return LCO(self.grid_data.get_product("LCO"))


class District(object):
    def __init__(self, name: str, primary: Location, secondary: Location, zone: Zone | None = None, station: Station | None = None, control: Location | None = None):
        self.name: str = name
        self.primary: Location = primary
        self.primary_forecast: Forecast = primary.get_forecast()
        self.secondary: Location = secondary
        self.secondary_forecast: Forecast = secondary.get_forecast()
        self.zone: Zone
        self.station: Station
        self.control: Location
        if zone is None:
            self.zone = primary.latlon.get_zone()
        else:
            self.zone = zone
        if station is None:
            self.station = primary.grid_data.get_station()
        else:
            self.station = station
        if control is None:
            self.control = Location(self.station.latlon)  # todo: optimize memory
        else:
            self.control = control
        self.control_forecast: Forecast = self.control.get_forecast()
        self.primary_observations: Observations = self.station.get_observations()
        self.fzl: FZL = primary.get_fzl()
        self.lco: LCO = primary.get_lco()

    def __repr__(self):
        return (f"District({self.name.__repr__()}, {self.primary.__repr__()}, {self.secondary.__repr__()}, "
                f"zone={self.zone.__repr__()}, station={self.station.__repr__()}, control={self.control.__repr__()})")

    def __str__(self):
        return f"{self.name}: (\n\t{self.primary}\n\t{self.secondary}\n\t{self.control}\n)"


def americanize(value: float, unit: str):
    if unit == "C":
        return value * 9/5 + 32
    elif unit == "mm":
        return value / 25.4
    elif unit == "kph":
        return value / 1.609344
    else:
        raise ValueError(f"unknown unit: {unit.__repr__()}")


def neural_net():
    pass


def snowday_score(area: District):
    pass


def fmt(value: float) -> str:
    return f"{floor(sigmoid_normal(value) * 100)}%"


def main():
    if check_ok():
        my_district: District = District(
            "District 1",
            Location(Point(sample_locations[0])),
            Location(Point(sample_locations[1])),
        )
        snowday_score(my_district)
        print(my_district)
        print(my_district.fzl.i)
        print(my_district.lco.i)


if __name__ == "__main__":
    t0 = time()
    main()
    print(call.num_calls)
    print(time() - t0)


# todo: good product names: HYD
# todo scrape power company's website
