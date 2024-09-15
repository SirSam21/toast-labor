from .time_entry import TimeEntry
from .utils import wage_to_id
import json


class EmployeeDict(dict):

    def add_entries(self, raw_entries):
        unowned_time_entries = []
        for re in raw_entries:
            id = wage_to_id(re["hourlyWage"])
            te = TimeEntry(re)
            warning = te.check()
            if id in self:
                self[id].time_entries.append(te)
                if warning != "":
                    self[id].warnings.append(warning)
            else:
                unowned_time_entries.append(te)

        if len(unowned_time_entries) > 0:
            print("unowned time entries:")
            for uote in unowned_time_entries:
                print(uote)
            print()

    def check_entries(self):
        for emp in self.values():
            emp.warnings = []
            for te in emp.time_entries:
                te.update_hours()
                warning = te.check()
                if warning != "":
                    emp.warnings.append(warning)

    def update_from_json_file(self, file_name):
        with open(file_name) as f:
            data = json.load(f)
            for id, emp in self.items():
                emp.update_from_json(data[id])
