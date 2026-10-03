import requests
from base64 import b64encode
from dotenv import load_dotenv
from datetime import datetime
import os
from windows_toasts import Toast, WindowsToaster

def seconds_to_hhmm(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"

def get_seconds_during_last_month(api_token, workspace_id, projec_id):
    start_date = datetime.today().replace(day=1).strftime("%Y-%m-%d")
    end_date = datetime.today().strftime("%Y-%m-%d")

    data = requests.post(f'https://api.track.toggl.com/reports/api/v3/workspace/{workspace_id}/projects/summary',
                            json={
                                "start_date": start_date,
                                "end_date": end_date
                            },
                            headers={
                                'content-type': 'application/json',
                                'Authorization' : 'Basic %s' %  b64encode(f"{api_token}:api_token".encode("utf-8")).decode("ascii")
                            })
    data_json = data.json()

    for data in data_json:
        if data["project_id"] == project_id:
            return data["tracked_seconds"]

def is_seconds_over_limit(spent_seconds, trigger_hours):
    hours = spent_seconds / 3600
    return hours >= trigger_hours


load_dotenv()

api_token = os.getenv("API_TOKEN")
workspace_id = os.getenv("WORKSPACE_ID")
project_id = int(os.getenv("PROJECT_ID"))
project_title = os.getenv("PROJECT_TITLE")
trigger_time_hours = int(os.getenv("TRIGGER_TIME_HOURS"))

monthly_seconds_for_project_id = get_seconds_during_last_month(api_token, workspace_id, project_id)

if is_seconds_over_limit(monthly_seconds_for_project_id, trigger_time_hours):
    toaster = WindowsToaster('Toggl Track Notifier')
    newToast = Toast()
    newToast.text_fields = [f"{project_title} current month spent time:", seconds_to_hhmm(monthly_seconds_for_project_id)]
    toaster.show_toast(newToast)

