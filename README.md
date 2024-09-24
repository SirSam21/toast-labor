# rbql query for employees.csv from toast:

select a['First Name'], a['Last Name'], a.GUID, a['Job GUIDs'], a.Wages where a.Wages != 0.00

clean up the data by removing headers, slap it in data/{restaurant}/employees.csv

# update the employee ids when a new employee is hired 
```bash
py update_employee_ids.py
```

# get the time entries for the pay period
```bash
py get_time_entries.py
```

# manually fix time entries in data/{restaurant}/time_entries/{year}/{pay_period}/entries_no_pickle.json
What you are looking for are mainly people who forgot to clock out or any other
anomalies.

# Calculate the hours for each employee
Make sure you have the cash tips for the pay period
```bash
py calculate.py
```
