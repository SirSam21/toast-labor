# rbql query for employees.csv from toast:

select a['First Name'], a['Last Name'], a.GUID, a['Job GUIDs'], a.Wages where a.Wages != 0.00

clean up the data, slap it in data/{restaurant}/employees.csv

# run py update_employee_ids.py

# run get_time_entries
# manually fix time entries in data/{restaurant}/{}

# run py calculate.py
