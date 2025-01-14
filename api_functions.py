import requests


class BadResponse(Exception):
    pass


def call(url: str) -> dict:
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise BadResponse(f"{response.status_code}")


def check_ok() -> bool:
    return call("https://api.weather.gov/")["status"] == "OK"
