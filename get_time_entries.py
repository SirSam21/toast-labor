from classes import ToastClient, Employee, EmployeeDict, CustomDatetimeHandler
import argparse
import classes.utils as utils
import csv
import jsonpickle
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta


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
            restaurant_id, first_name, last_name, ext_id, ref_id, wage_id, job_id = row
            employees[int(wage_id)] = Employee(first_name,
                                               last_name,
                                               ext_id,
                                               int(wage_id),
                                               restaurant_id,
                                               job_id,
                                               ref_id)

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

    print("please enter starting and ending date mm/dd/yy")
    start = input("start: ")
    end = input("end: ")

    start_date, end_date = utils.get_bounding_dates(start, end)

    y = start_date.date().year
    s = "{}-{}".format(start_date.date().month, start_date.date().day)
    e_date = end_date - timedelta(days=1)
    e = "{}-{}".format(e_date.date().month, e_date.date().day)
    dates = "{}/{}_{}".format(y, s, e)

    raw_entries = client.get_raw_time_entries(restaurant_info["externalId"],
                                              start_date,
                                              end_date)
    employees = get_employees(rest_name)
    employees.add_entries(raw_entries)

    data_path = Path('/Users/sam/dojo/python/toast-labor/data')
    archive_path = data_path / 'archive'
    out_file_name = data_path / rest_name / \
        'time_entries' / dates / 'entries_class.json'

    arch_file_name = archive_path / rest_name / \
        'time_entries' / dates / 'entries_class.json'

    no_pickle = data_path / rest_name / \
        'time_entries' / dates / 'entries_no_pickle.json'

    arch_no_pickle = archive_path / rest_name / \
        'time_entries' / dates / 'entries_no_pickle.json'

    paths = [out_file_name, arch_file_name, no_pickle, arch_no_pickle]

    for p in paths:
        p.parent.mkdir(parents=True, exist_ok=True)

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
