from classes import ToastClient, Employee, EmployeeDict, CustomDatetimeHandler
import argparse
import classes.utils as utils
import csv
import jsonpickle
from dotenv import load_dotenv
from datetime import datetime


def get_toast_client():
    return ToastClient()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    parser.add_argument('-u', '--update_file')

    args = parser.parse_args()

    return args


def get_employees(restaurant_name):

    employees = EmployeeDict()

    file_name = "data/{}/employee_ids.csv".format(restaurant_name)
    with open(file_name) as f:
        reader = csv.reader(f)
        for row in reader:
            row = [x.strip() for x in row]
            restaurant_id, first_name, last_name, wage_id, guid, job_id = row
            employees[int(wage_id)] = Employee(first_name,
                                               last_name,
                                               guid,
                                               int(wage_id),
                                               restaurant_id,
                                               job_id)

    return employees


def choose_restaurant():
    restaurants_info = utils.get_restaurants_info()
    for i, r in enumerate(restaurants_info):
        print(f'{i}: {r["name"]}')
    print("Please choose a restaurant:")

    ind = -1
    while True:
        ind = int(input())
        if ind > len(restaurants_info) or ind < 0:
            print("invalid store id")
        else:
            break
    return restaurants_info[ind]


def aggregate_data():
    client = get_toast_client()

    restaurant_info = choose_restaurant()

    rest_name = restaurant_info["name"]
    start_date, end_date = utils.get_bounding_dates()

    raw_entries = client.get_raw_time_entries(restaurant_info["externalId"],
                                              start_date,
                                              end_date)
    employees = get_employees(rest_name)
    employees.add_entries(raw_entries)

    out_file_name = 'data/{}/time_entries/entries_class.json'.format(
        rest_name)
    arch_file_name = 'data/archive/{}/time_entries/entries_class.json'.format(
        rest_name
    )
    no_pickle = 'data/{}/time_entries/entries_no_pickle.json'.format(rest_name)
    arch_no_pickle = 'data/archive/{}/time_entries/entries_no_pickle.json'.format(
        rest_name
    )

    with open(out_file_name, 'w') as f:
        f.write(jsonpickle.encode(employees))

    with open(arch_file_name, 'w') as f:
        f.write(jsonpickle.encode(employees))

    with open(no_pickle, 'w') as f:
        f.write(jsonpickle.encode(employees, unpicklable=False))

    with open(arch_no_pickle, 'w') as f:
        f.write(jsonpickle.encode(employees, unpicklable=False))


def fix_data(file_name, update_file):

    with open(file_name) as f:
        employees = jsonpickle.decode(f.read())

    with open(update_file) as f:
        employees.update_from_json_file(update_file)

    employees.check_entries()

    with open(file_name, 'w') as f:
        f.write(jsonpickle.encode(employees))

    with open(update_file, 'w') as f:
        f.write(jsonpickle.encode(employees, unpicklable=False))


def get_time_entries():
    load_dotenv()
    args = get_args()

    if args.file is None:
        aggregate_data()
    else:
        fix_data(args.file, args.update_file)


if __name__ == "__main__":
    jsonpickle.handlers.register(datetime, CustomDatetimeHandler)
    get_time_entries()
