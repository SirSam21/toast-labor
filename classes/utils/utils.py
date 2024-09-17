from datetime import datetime, timedelta
import json
from pathlib import Path


def get_bounding_dates(start, end):

    start = start + "-0700"
    end = end + "-0700"
    start_date = datetime.strptime(start, '%m/%d/%y%z')
    end_date = datetime.strptime(
        end, '%m/%d/%y%z') + timedelta(days=1)

    return start_date, end_date


def get_restaurants_info():
    restaurants = {}
    with open("data/restaurants.json") as f:
        restaurants = json.load(f)

    return restaurants


def wage_to_id(wage):
    if isinstance(wage, float):
        return int(wage*100)
    elif isinstance(wage, str):
        return int(wage.replace(".", ""))
    else:
        print("could not parse wage to id:", wage)

    return -1


def toast_date_format(time):
    # "2016-01-01T14:13:12.000-0000"
    return time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "-0700"


def get_time_entries_path(restaurant_name):
    data_path = Path('/Users/sam/dojo/python/toast-labor/data')
    p = data_path / restaurant_name / 'time_entries'
    return p
