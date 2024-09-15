import requests
from .utils import toast_date_format
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os


class ToastClient:
    def __init__(self, url="https://ws-api.toasttab.com"):
        self._secret = os.environ.get('CLIENT_SECRET')
        self._client_id = os.environ.get('CLIENT_ID')
        self._url = url
        self._token = self.get_auth_token()
        self.end_date = datetime.now(tz=ZoneInfo("America/Los_Angeles"))
        self.start_date = self.end_date - timedelta(weeks=2)

    def get_auth_token(self):

        path = "/authentication/v1/authentication/login"

        payload = {
            "clientId": self._client_id,
            "clientSecret": self._secret,
            "userAccessType": "TOAST_MACHINE_CLIENT"
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            self.get_url(path), json=payload, headers=headers)

        data = response.json()
        return data["token"]["accessToken"]

    def get_raw_time_entries(self, restaurant_id, start_date, end_date):
        path = "/labor/v1/timeEntries"
        end = toast_date_format(end_date)
        start = toast_date_format(start_date)
        query = {
            "endDate": end,
            "startDate": start,
        }

        headers = {
            "Toast-Restaurant-External-ID": restaurant_id,
            "Authorization": "Bearer {}".format(self._token)
        }

        response = requests.get(self.get_url(
            path), headers=headers, params=query)

        return response.json()

    def get_job_entries(self, restaurant_id):
        path = "/labor/v1/jobs"

        headers = {
            "Toast-Restaurant-External-ID": restaurant_id,
            "Authorization": "Bearer {}".format(self._token)
        }

        response = requests.get(self.get_url(
            path), headers=headers)

        return response.json()

    def get_url(self, path):
        return self._url + path
