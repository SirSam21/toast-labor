import jsonpickle
import math
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime
from classes import CustomDatetimeHandler
from get_time_entries import choose_restaurant


def summary(employee):
    regular_hours = 0
    overtime_hours = 0
    for te in employee.time_entries:
        regular_hours += te.regular_hours
        overtime_hours += te.overtime_hours

    fmt = "name: {} {}\nregular hours: {: .2f}\not hours: {: .2f}\ncredit tips: {: .2f}\ncash tips: {: .2f}\n"

    return fmt.format(
        employee.first_name,
        employee.last_name,
        regular_hours,
        overtime_hours,
        employee.credit_tips,
        employee.cash_tips)


def calculate():
    restaurant_info = choose_restaurant()
    restaurant_name = restaurant_info["name"]
    server_tip_split = restaurant_info["jobs"]["server"]["tipPool"]
    cook_tip_split = restaurant_info["jobs"]["cook"]["tipPool"]
    server_id = restaurant_info["jobs"]["server"]["guid"]
    cook_id = restaurant_info["jobs"]["cook"]["guid"]

    entries_file = 'data/{}/time_entries/entries_class.json'.format(
        restaurant_name)
    update_file = 'data/{}/time_entries/entries_no_pickle.json'.format(
        restaurant_name)

    with open(entries_file, 'r') as f:
        employees = jsonpickle.decode(f.read())

    with open(update_file) as f:
        employees.update_from_json_file(update_file)

    cooks = defaultdict(int)
    servers = defaultdict(int)
    credit_tips = defaultdict(float)
    leftover = 0

    for employee in employees.values():
        if employee.job_id == cook_id:
            working_dict = cooks
        elif employee.job_id == server_id:
            working_dict = servers

        for k, v in employee.get_times().items():
            working_dict[k] += v

        for k, v in employee.get_tips().items():
            credit_tips[k] += v

    cash_tips = defaultdict(float)
    print("please enter cash tips:")
    for date in sorted(cooks.keys()):
        cash_tips[date] = float(input('{}: '.format(date)))
        leftover += cash_tips[date]

    for employee in employees.values():
        if employee.job_id == cook_id:
            working_dict = cooks
            split = cook_tip_split
        elif employee.job_id == server_id:
            working_dict = servers
            split = server_tip_split

        employee.credit_tips = 0
        employee.cash_tips = 0
        for k, v in employee.get_times().items():
            r = split * v / working_dict[k]
            employee.credit_tips += credit_tips[k] * r
            employee.cash_tips += math.floor(cash_tips[k] * r)
            leftover -= math.floor(cash_tips[k] * r)

    out_file = 'data/{}/tmp_complete.txt'.format(restaurant_name)
    with open(out_file, "w") as f:
        for employee in employees.values():
            employee.cash_tips += math.floor(leftover / len(employees))
            f.write(summary(employee))
            f.write("\n")
        f.write("\n")
        f.write("leftover tips: ${:.2f}".format(leftover % len(employees)))


if __name__ == "__main__":
    load_dotenv()
    jsonpickle.handlers.register(datetime, CustomDatetimeHandler)
    calculate()
