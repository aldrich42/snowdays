from api_functions import call_json


class Point(object):
    def __init__(self, latlon: str):
        self.latitude: str
        self.longitude: str
        self.latitude, self.longitude = tuple(latlon.split(","))


class GridPoint(object):
    def __init__(self, mun: str, state: str, wfo: str, grid_x: str, grid_y: str):
        self.mun: str = mun
        self.state: str = state
        self.wfo: str = wfo
        self.grid_x: str = grid_x
        self.grid_y: str = grid_y


class Zone(object):
    def __init__(self, zone_id: str, name: str):
        self.id: str = zone_id
        self.name: str = name


class Station(object):
    def __init__(self, station_id: str, name: str):
        self.id: str = station_id
        self.name: str = name


class Place(object):
    def __init__(self, latitude: str, longitude: str, municipality: str | None = None, state: str | None = None,
                 wfo: str | None = None, x: str | None = None, y: str | None = None,
                 observation_station: str | None = None, zone_name: str | None = None, zone_id: str | None = None):
        self.latitude: str = latitude
        self.longitude: str = longitude
        self.municipality: str = municipality
        self.state: str = state
        self.wfo: str = wfo
        self.x: str = x
        self.y: str = y
        self.observation_station: str = observation_station
        self.zone_name: str = zone_name
        self.zone_id: str = zone_id
        if None in {municipality, state, wfo, x, y}:
            self.municipality, self.state, self.wfo, self.x, self.y = self.find_place()
        if zone_name is None or zone_id is None:
            self.zone_name, self.zone_id = self.find_zone()
        if observation_station is None:
            self.observation_station = self.find_observation_station()

    def find_place(self) -> (str, str, str, str, str):
        properties = call_json(self.url_points())["properties"]
        return (properties["relativeLocation"]["properties"]["city"],
                properties["relativeLocation"]["properties"]["state"],
                properties["gridId"], properties["gridX"], properties["gridY"])

    def find_zone(self) -> (str, str):
        properties = call_json(self.url_zones())["features"][0]["properties"]
        return properties["name"], properties["id"]

    def find_observation_station(self) -> str:
        station = call_json(self.url_observation_stations())["features"][0]["properties"]["stationIdentifier"]
        return station

    def url_points(self) -> str:
        return f"https://api.weather.gov/points/{self.latitude},{self.longitude}"

    def url_zones(self) -> str:
        return f"https://api.weather.gov/zones?type=land&point={self.latitude},{self.longitude}&include_geometry=false"

    def url_observation_stations(self) -> str:
        return f"https://api.weather.gov/gridpoints/{self.wfo}/{self.x},{self.y}/stations"

    def url_data(self) -> str:
        return f"https://api.weather.gov/gridpoints/{self.wfo}/{self.x},{self.y}"

    def url_forecast(self) -> str:
        return f"https://api.weather.gov/gridpoints/{self.wfo}/{self.x},{self.y}/forecast"

    def url_hourly_forecast(self) -> str:
        return f"https://api.weather.gov/gridpoints/{self.wfo}/{self.x},{self.y}/forecast/hourly"

    def url_observations(self) -> str:
        return f"https://api.weather.gov/stations/{self.observation_station}/observations/"

    def url_mapclick(self) -> str:
        return f"https://forecast.weather.gov/MapClick.php?lat={self.latitude}&lon={self.longitude}&FcstType=json"

    def url_headlines(self) -> str:
        return f"https://api.weather.gov/offices/{self.wfo}/headlines"

    def url_alerts(self) -> str:
        return f"https://api.weather.gov/alerts?zone={self.zone_id}"

    def get_data(self) -> dict:
        return call_json(self.url_data())

    def get_forecast(self) -> dict:
        return call_json(self.url_forecast())

    def get_hourly_forecast(self) -> dict:
        return call_json(self.url_hourly_forecast())

    def get_mapclick(self) -> dict:
        return call_json(self.url_mapclick())

    def get_observations(self) -> dict:
        return call_json(self.url_observations())

    def get_headlines(self) -> dict:
        return call_json(self.url_headlines())

    def get_alerts(self) -> dict:
        return call_json(self.url_alerts())


class Location(object):
    def __init__(self):
        pass


class District(object):
    def __init__(self):
        pass
