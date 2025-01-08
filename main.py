import datetime
import pytz
import random


def cm_to_in(cm: float) -> float:
    return cm / 2.54


def c_to_f(c: float) -> float:
    return c * 9/5 + 32


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
