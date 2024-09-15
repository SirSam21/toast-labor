from .utils import wage_to_id
from datetime import datetime
from zoneinfo import ZoneInfo

toast_date_format = '%Y-%m-%dT%H:%M:%S.%f%z'
warning_date_format = '%m/%d/%y'
repr_date_format = '%m/%d/%y %H:%M:%S'
tz = ZoneInfo("America/Los_Angeles")


class TimeEntry:
    def __init__(self, raw_time_entry):

        # "inDate": "2024-09-07T22:58:33.933+0000",
        # "outDate": "2024-09-08T11:00:00.000+0000",
        # "overtimeHours": 4.02,
        # "breaks": [],
        # "employeeReference": {
        # "guid": "1a180edb-fbe0-4182-92c0-40329ae90875",
        # },
        # "regularHours": 8.0,
        # "jobReference": {
        # "guid": "53d5ad82-1f4a-463b-8006-fed2776a080d",
        # },
        # "hourlyWage": 0.13,
        # "nonCashTips": 5.0,
        # "autoClockedOut": true
        self.in_date = datetime.strptime(
            raw_time_entry["inDate"], toast_date_format).astimezone(tz)
        self.out_date = datetime.strptime(
            raw_time_entry["outDate"], toast_date_format).astimezone(tz)
        self.overtime_hours = float(raw_time_entry["overtimeHours"])
        self.total_break_time = 0
        self.aggregate_break_time(raw_time_entry["breaks"])
        self.guid = raw_time_entry["employeeReference"]["guid"]
        self.regular_hours = float(raw_time_entry["regularHours"])
        self.job_guid = raw_time_entry["jobReference"]["guid"]
        self.wage_id = wage_to_id(raw_time_entry["hourlyWage"])
        self.credit_tips = float(raw_time_entry["nonCashTips"])
        self.auto_clocked_out = bool(raw_time_entry["autoClockedOut"])

    def check(self):
        """
        checks that time entry follows these rules, otherwise returns warnings:
        - if hours >5 need to have a 30 min break
        - if hours >10 need to have a 60 min break
        - check automatic clockout did not occur
        """
        date_str = self.in_date.strftime(warning_date_format)

        if self.auto_clocked_out:
            return "{}: auto clock out occurred".format(date_str)
        elif self.overtime_hours > 2 and self.total_break_time < 3600:
            return "{}: 10+ hours without sufficient break".format(date_str)
        elif self.regular_hours > 5 and self.total_break_time < 1800:
            return "{}: 5+ hours without sufficient break".format(date_str)
        elif self.total_break_time > 3600:
            return "{}: long break".format(date_str)
        else:
            return ""

    def aggregate_break_time(self, breaks):
        total_break_time = 0
        for br in breaks:
            start = datetime.strptime(br["inDate"], toast_date_format)
            end = datetime.strptime(br["outDate"], toast_date_format)
            delta = end - start
            total_break_time += round(delta.total_seconds() / 3600, 2)

        self.total_break_time = total_break_time

    def update_hours(self):
        delta = self.out_date - self.in_date
        total_h = round(delta.total_seconds() / 3600, 2)
        break_h = self.total_break_time
        reg_h = min(total_h - break_h, 8)
        overtime_h = max(total_h - break_h - 8, 0)

        if total_h > 10 and break_h < 1:
            overtime_h -= 1 - break_h
            break_h = 1

            # will never happen
            if overtime_h < 0:
                reg_h -= overtime_h
                overtime_h = 0

        self.total_break_time = break_h
        self.regular_hours = reg_h
        self.overtime_hours = overtime_h

    def __repr__(self):
        in_date = self.in_date.strftime(repr_date_format)
        out_date = self.out_date.strftime(repr_date_format)
        return """
in_date: {}
out_date: {}
ot hours: {}
breaks: {}
guid: {}
regular_hours: {}
job_guid: {}
wage_id: {}
credit_tips: {}
auto_clocked_out: {}""".format(
            in_date,
            out_date,
            self.overtime_hours,
            self.total_break_time,
            self.guid,
            self.regular_hours,
            self.job_guid,
            self.wage_id,
            self.credit_tips,
            self.auto_clocked_out)
