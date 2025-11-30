#!/home/dylan/code/calme/calmevenv/bin/python

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os.path
import argparse
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

RED = '\033[31m'
GREEN = '\033[32m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
RESET = '\033[0m'

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def auth_user():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    calme_path = Path(__file__).resolve().parent
    
    if os.path.exists(calme_path / "token.json"):
        creds = Credentials.from_authorized_user_file(calme_path / "token.json", SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                calme_path / "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(calme_path / "token.json", "w") as token:
                token.write(creds.to_json())
                
    return creds

def list_events(amount = 10):
    creds = auth_user()

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        format = "%Y-%m-%dT%H:%M:%SZ"
        timezone = ZoneInfo('America/Toronto')
        now = (datetime.now(timezone)).strftime(format)
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=amount,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print(RED + "No upcoming events found." + RESET)
            return

        print(f"{"Event ID".center(80, '.')}{"Event Date".center(40, '.')}{"Event Title".center(40, '.')}")
        for event in events:
            id = event["id"]
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(f"{CYAN + id.ljust(80) + RESET}{MAGENTA + start.center(40) + RESET}{GREEN + event["summary"][:40].ljust(40) + RESET}")
            print("-".center(160, '-'))

    except HttpError as error:
        print(RED + f"An error occurred: {error}" + RESET)


def validate_date(time):
    format = "%Y-%m-%dT%H:%M:%S"
    
    try:
        datetime.strptime(time, format)
        return True
    except ValueError:
        return False

def format_event_date(time = None, minute = None):
    format = "%Y-%m-%dT%H:%M:%S"
    
    start = (datetime.now() + timedelta(minutes=30)).strftime(format)
    end = (datetime.now() + timedelta(minutes=45)).strftime(format)
    
    if minute:
        start = (datetime.now() + timedelta(minutes=minute)).strftime(format)
        end = (datetime.now() + timedelta(minutes=minute+15)).strftime(format)
        
    if time:
        valid = validate_date(time)
        if not valid:
            print(RED + f"Invalid Date Format! Example: 2025-12-31T14:30:45" + RESET)
            return
        
        upcoming = datetime.strptime(time, format)
        start = upcoming.strftime(format)
        end = (upcoming + timedelta(minutes=15)).strftime(format)
        
    return start, end

def create_event(time = None, min = None, remind = 15, note = "Empty Event Created"):
    creds = auth_user()

    start, end = format_event_date(time, min)

    try:
        service = build("calendar", "v3", credentials=creds)
        event = {
            'summary': note[:20],
            #'location': '',
            'description': note,
            'start': {
                'dateTime': start,
                'timeZone': 'America/Toronto',
            },
            'end': {
                'dateTime': end,
                'timeZone': 'America/Toronto',
            },
            #'recurrence': [
            #],
            #'attendees': [
            #],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': remind},
                    {'method': 'popup', 'minutes': int(remind/2)},
                ],
            },
        }
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(f"Event Created: ID: {CYAN + event.get('id') + RESET}, Date: {MAGENTA + start + RESET}, Note: {GREEN + event.get('description') + RESET}")
    except HttpError as error:
        print(RED + f"An error occurred: {error}" + RESET)

def delete_event(event_id):
    creds = auth_user()
    try:
        service = build("calendar", "v3", credentials=creds)
        
        event = service.events().get(calendarId="primary", eventId=event_id).execute()
        
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(f"Event to Delete: ID: {CYAN + event.get('id') + RESET}, Date: {MAGENTA + start + RESET}, Note: {GREEN + event.get('description') + RESET}")
        confirm_delete = input("Confirm Delete? (y/n): ")
        
        if confirm_delete.lower() == "y":
            service.events().delete(calendarId="primary", eventId=event_id).execute()
            print("Event Deleted.")
        else:
            print("Event Not Deleted.")
    except HttpError as error:
        print(RED + f"An error occurred: {error}" + RESET)


def parser():
    parser = argparse.ArgumentParser(description="Leave yourself gcal notes for funsies.")
    parser.add_argument("-t", "--time", help="Schedule event at this date and time. Format: 2025-12-31T18:30:45", type=str)
    parser.add_argument("-m", "--min", help="Schedule event N minutes from now. Minutes: 30, 180, 57", type=int, default=30)
    parser.add_argument("-r", "--remind", help="Set the event reminder. Minutes: 15, 30, 60", type=int, default=15)
    parser.add_argument("-n", "--note", help="Enter the task title/description", type=str, default="Empty Event Created")
    parser.add_argument("-l", "--list", help="List the next N events by the number you pass.", type=int)
    parser.add_argument("-d", "--delete", help="Pass the Event ID in to delete it.", type=str)
    
    return parser
    
if __name__ == "__main__":
    parser = parser()
    args = parser.parse_args()
    
    if args.list:
        list_events(args.list)
    elif args.delete:
        delete_event(args.delete)
    else:
        create_event(
            args.time, 
            args.min, 
            args.remind, 
            args.note
        )
