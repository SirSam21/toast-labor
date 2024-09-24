import json
from datetime import datetime
from .time_entry import TimeEntry

standard_fmt_1 = '%Y-%m-%d %H:%M:%S.%f%z'
standard_fmt_2 = '%Y-%m-%d %H:%M:%S%z'


class Employee:
    def __init__(self, first_name, last_name, ext_id,
                 restaurant_id, job_id, ref_id=0):
        self.first_name = first_name
        self.last_name = last_name
        # id found in csv files
        self.ext_id = ext_id
        # id found in time entry employee references
        self.ref_id = ref_id
        # id used to connect external id to ref id
        self.restaurant_id = restaurant_id
        self.job_id = job_id
        self.credit_tips = 0
        self.cash_tips = 0
        self.warnings = []
        self.hours_offset = 0
        self.overtime_offset = 0
        self.notes = ""
        self.time_entries = []

    def to_csv(self):
        return [
            self.restaurant_id,
            self.first_name,
            self.last_name,
            self.ext_id,
            self.ref_id,
            self.job_id
        ]

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def get_times(self):
        date_fmt = '%m/%d/%y'
        times = {}
        for te in self.time_entries:
            date = te.in_date.strftime(date_fmt)
            if date not in times:
                times[date] = te.regular_hours + te.overtime_hours
            else:
                times[date] += te.regular_hours + te.overtime_hours

        return times

    def get_tips(self):
        date_fmt = '%m/%d/%y'
        tips = {}
        for te in self.time_entries:
            date = te.in_date.strftime(date_fmt)
            if date not in tips:
                tips[date] = te.credit_tips
            else:
                tips[date] += te.credit_tips

        return tips

    def update_from_json(self, data):
        self.hours_offset = data["hours_offset"]
        self.overtime_offset = data["overtime_offset"]
        self.notes = data["notes"]

        for i, dte in enumerate(data["time_entries"]):
            if len(self.time_entries) - 1 < i:
                te = TimeEntry()
                te.job_guid = dte["job_guid"]
                self.time_entries.append(te)

            try:
                self.time_entries[i].in_date = datetime.strptime(dte["in_date"],
                                                                 standard_fmt_1)
            except ValueError:
                self.time_entries[i].in_date = datetime.strptime(dte["in_date"],
                                                                 standard_fmt_2)
            try:
                self.time_entries[i].out_date = datetime.strptime(dte["out_date"],
                                                                  standard_fmt_1)
            except ValueError:
                self.time_entries[i].out_date = datetime.strptime(dte["out_date"],
                                                                  standard_fmt_2)

            self.time_entries[i].auto_clocked_out = dte["auto_clocked_out"]

            self.time_entries[i].update_hours()

    # def summary(self):
    # regular_hours = 0
    # overtime_hours = 0
    # for te in self.time_entries:
    # regular_hours += te.regular_hours
    # overtime_hours += te.overtime_hours

    # return """
    # name: {} {}
    # regular hours: {}
    # ot hours: {}
    # credit tips: {}
    # cash tips: {}""".format(
    # self.first_name,
    # self.last_name,
    # regular_hours,
    # overtime_hours,
    # credit_tips,
    # cash_tips)
