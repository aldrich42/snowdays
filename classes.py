from api_functions import call_json


headers = None


class Point(object):
    def __init__(self, latlon_str: str):
        self.latitude: str
        self.longitude: str
        self.latitude, self.longitude = tuple(latlon_str.split(","))

    def get_grid_data(self):
        url = f"https://api.weather.gov/points/{self.latitude},{self.longitude}"
        data = call_json(url, headers=headers)["properties"]
        return GridPoint(data["relativeLocation"]["properties"]["city"],
                         data["relativeLocation"]["properties"]["state"],
                         data["gridId"], data["gridX"], data["gridY"], data["radarStation"])

    def get_zone(self):
        url = f"https://api.weather.gov/zones?type=land&point={self.latitude},{self.longitude}&include_geometry=false"
        data = call_json(url, headers=headers)["features"][0]["properties"]
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
        data = call_json(url, headers=headers)["features"][0]["properties"]
        return Station(data["stationIdentifier"], data["name"])

    def get_forecast_json(self):
        url = f"https://api.weather.gov/gridpoints/{self.wfo}/{self.grid_x},{self.grid_y}"
        return call_json(url, headers=headers)

    def get_headlines_json(self):
        url = f"https://api.weather.gov/offices/{self.wfo}/headlines"
        return call_json(url, headers=headers)


class Zone(object):
    def __init__(self, zone_id: str, name: str):
        self.id: str = zone_id
        self.name: str = name

    def get_alerts_json(self):
        url = f"https://api.weather.gov/alerts?zone={self.id}"
        return call_json(url, headers=headers)


class Station(object):
    def __init__(self, station_id: str, name: str):
        self.id: str = station_id
        self.name: str = name

    def get_observations_json(self):
        url = f"https://api.weather.gov/stations/{self.id}/observations"
        return call_json(url, headers=headers)


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


class District(object):
    def __init__(self, center: Location, *margin: Location):
        self.center: Location = center
        self.margin: tuple[Location, ...] = margin
