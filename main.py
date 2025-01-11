import datetime
import pytz
import random
import requests


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
        raise ValueError(f"Unknown temperature conversion: {(from_unit,to_unit).__repr__()}")


def chance_of_snow_day(predicted_temperature: float, predicted_snowfall: float) -> float:
    dt: datetime.datetime = datetime.datetime.now(tz=pytz.timezone("EST"))

    # mathy math

    return random.random()


# types of outcomes that we can expect:
# snow day
# virtual day
# 2 hour delay
# 1 hour delay
# early dismissal (rare)
# normal day
# special day (weekend, holiday, whatever)


print(f"{chance_of_snow_day(-2.5, 10.0)*100:.0f}%")
