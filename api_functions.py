import requests


class BadResponse(Exception):
    pass


def call(url: str, headers: dict | None) -> requests.Response:
    response = requests.get(url, headers=headers)
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
