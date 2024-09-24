import csv
from dotenv import load_dotenv
from classes import ToastClient, Employee, EmployeeDict
from classes.utils import get_bounding_dates, get_restaurants_info
from pathlib import Path


def get_wage_id_to_ref_id(time_entries):

    wage_to_ref = {}
    for te in time_entries:
        ref_id = te["employeeReference"]["guid"]
        wage_id = int(te["hourlyWage"]*100)
        wage_to_ref[wage_id] = ref_id

    return wage_to_ref


def update_employee_ids():

    restaurants = get_restaurants_info()
    client = ToastClient()
    print("please enter starting and ending date mm/dd/yy")
    start = input("start: ")
    end = input("end: ")

    start, end = get_bounding_dates(start, end)

    for r in restaurants:
        employees = EmployeeDict()
        restaurant_path = Path('data') / r["name"]

        file_name = restaurant_path / 'employees.csv'
        with open(file_name) as f:
            reader = csv.reader(f)
            for row in reader:
                row = [x.strip() for x in row]
                first_name, last_name, external_guid, job_id, wage_id = row
                wage_id = int(str(wage_id).split(";")[0].replace(".", ""))
                job_id = str(job_id).split(";")[0]
                emp = Employee(first_name,
                               last_name,
                               external_guid,
                               r["externalId"],
                               job_id)
                employees[wage_id] = emp

        time_entries = client.get_raw_time_entries(r["externalId"], start, end)
        wage_to_ref = get_wage_id_to_ref_id(time_entries)

        for wid, emp in employees.items():
            if wid in wage_to_ref:
                emp.ref_id = wage_to_ref[wid]
            else:
                emp.ref_id = "none"

        employee_ids_path = restaurant_path / 'employee_ids.csv'
        with open(employee_ids_path, 'w') as csvfile:
            writer = csv.writer(csvfile)
            for v in employees.values():
                writer.writerow(v.to_csv())


if __name__ == "__main__":
    load_dotenv()
    update_employee_ids()
    print("c;")
