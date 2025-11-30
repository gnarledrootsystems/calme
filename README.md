# CalMe

A simple script to add/list/delete events from your Google Calendar from the terminal. Cause why not?

<img width="876" height="47" alt="calme" src="https://github.com/user-attachments/assets/b3603f8c-c48d-4013-926d-da861f1d1eb5" />

## Setup 
1. For instructions to setup Google Auth follow: https://developers.google.com/workspace/calendar/api/quickstart/python
   1. You will need to add whatever email you want to test with to the group of local testers.
   2. Once you set that up, download the credentials file.
   3. Move it to the calme project root
   4. Rename it to `credentials.json`
   5. `token.json` will get created automatically after the first time you Authenticate yourself running the script.
   6. To re-authenticate, delete `token.json`

2. In the project root, create your venv
   1. Run: `python3 -m venv calmevenv`
   2. If you give it a different name, or a different file location you will need to update the shebang in `calme.py`

3. Go into your `calmevenv` and run `pip3`
   1. Run: `source calmevenv/bin/activate`
   2. Run: `pip3 install -r requirements.txt`
   3. Exit the venv environment: `deactivate`

5. Make `calme.py` executable
   1. Run `sudo chmod +x calme.py` 

6. Create a symlink for exec funsies
   1. Run: `ln -s path/to/calme/calme.py /usr/local/bin/calme.py`
   2. Or whichever pathing area you wish that is included in `$PATH`
   
7. Create events anywhere!
   1. Once you have the symlink set up, you can call `calme.py` from anywhere
   2. Run: `calme.py -n "Hello World!"`

## Options
1. "-t", "--time"
   1. Pass the time you want the event to start at. The end time will be +15 Minutes.
   2. Format: 2025-12-31T18:30:45
   
2. "-m", "--min"
   1. Rather than passing a full date, if you want to set an event N minutes in the future use this flag.
   2. Format (int): 30, 27, 60, 180 ...

3. "-r", "--remind"
   1. Sets the Reminder time to send you an email and notification. By default this is 15 minutes for email, and notifications are N/2.
   2. Format (int): 15, 30, 27, 60 ...
   
4. "-n", "--note"
   1. The Event Title/Body
   
5. "-l", "--list"
   1. This will list N future events. Default is 10.
   2. Format (int): 5, 10, 3278 ...
   
6. "-d", "--delete"
   1. This will delete an event from your calendar by passing the eventId (be careful!)
