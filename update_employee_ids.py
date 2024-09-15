import csv
from dotenv import load_dotenv
from classes import ToastClient, Employee
from classes.utils import get_bounding_dates, get_restaurants_info

url = "https://ws-api.toasttab.com"


def get_wage_id_to_int_id(time_entries):

    wage_id_to_int_id = {}
    for te in time_entries:
        int_guid = te["employeeReference"]["guid"]
        wage_id = int(te["hourlyWage"]*100)
        wage_id_to_int_id[wage_id] = int_guid

    return wage_id_to_int_id


def update_employee_ids():

    restaurants = get_restaurants_info()
    client = ToastClient()
    start, end = get_bounding_dates()

    for r in restaurants:
        ext_id_to_employee = {}
        wage_id_to_ext_id = {}
        file_name = "data/{}/employees.csv".format(r["name"])
        with open(file_name) as f:
            reader = csv.reader(f)
            for row in reader:
                row = [x.strip() for x in row]
                first_name, last_name, external_guid, job_id, wage_id = row
                wage_id = int(str(wage_id).split(";")[0].replace(".", ""))
                job_id = str(job_id).split(";")[0]
                ext_id_to_employee[external_guid] = Employee(first_name,
                                                             last_name,
                                                             external_guid,
                                                             wage_id,
                                                             r["externalId"],
                                                             job_id)
                wage_id_to_ext_id[wage_id] = external_guid

        time_entries = client.get_raw_time_entries(r["externalId"], start, end)
        w2i = get_wage_id_to_int_id(time_entries)
        i2e = {}
        for w_id, i_id in w2i.items():
            if w_id in wage_id_to_ext_id:
                i2e[i_id] = ext_id_to_employee[wage_id_to_ext_id[w_id]]

        file_name = "data/{}/employee_ids.csv".format(r["name"])
        with open(file_name, 'w') as csvfile:
            writer = csv.writer(csvfile)
            for k, v in i2e.items():
                writer.writerow(v.to_csv())


if __name__ == "__main__":
    load_dotenv()
    update_employee_ids()
    print("c;")
