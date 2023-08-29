import json
from django.contrib import messages
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from django.core.mail import  EmailMessage
from django.http import HttpResponse, request , FileResponse
from staffingapp.settings import CREDENTIALS_FILE
from zoomus import ZoomClient
from datetime import datetime
import http.client
from staffingapp.settings import ZOOM_TOKEN, ZOOM_API_KEY, ZOOM_API_SECRET

def zoom_users(request):
    conn = http.client.HTTPSConnection("api.zoom.us")
    headers = {
        'authorization': "Bearer " + str(ZOOM_TOKEN),
        'content-type': "application/json"
    }
    conn.request("GET", "/v2/users?status=active&page_size=30&page_number=1", headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return HttpResponse("============" + str(data.decode("utf-8")))


def zoom_meetings(request):
    client = ZoomClient(ZOOM_API_KEY, ZOOM_API_SECRET)
    user_list_response = client.user.list()
    user_list = json.loads(user_list_response.content)

    for user in user_list['users']:
        user_id = user['id']
        print(json.loads(client.meeting.list(user_id=user_id).content))

    conn = http.client.HTTPSConnection("api.zoom.us")
    headers = {
        'authorization': "Bearer " + str(ZOOM_TOKEN),
        'content-type': "application/json"
    }
    conn.request("GET", "/v2/users/" + str(user_id) + "/meetings", headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return HttpResponse(data.decode("utf-8"))



def zoom_client(request):
    client = ZoomClient(ZOOM_API_KEY, ZOOM_API_SECRET)
    print(client)
    user_list_response = client.user.list()
    user_list = json.loads(user_list_response.content)

    for user in user_list['users']:
        user_id = user['id']
        print(json.loads(client.meeting.list(user_id=user_id).content))

    return HttpResponse("============" + str(user_list))


def list_zoom_meeting(request):
    client = ZoomClient(ZOOM_API_KEY, ZOOM_API_SECRET)
    user_list_response = client.meeting.list()
    user_list = json.loads(user_list_response.content)

    for user in user_list['meetings']:
        print(json.loads(client.meeting.list().content))

    return HttpResponse("============" + str(user_list))

def zoom_meeting_create(zoomObj):
    client = ZoomClient(zoomObj.zoom_api_key, zoomObj.zoom_api_secret)
    print(client)
    user_list_response = client.user.list()
    user_list = json.loads(user_list_response.content)

    for user in user_list['users']:
        user_id = user['id']
        # print(json.loads(client.meeting.list(user_id=user_id).content))

    conn = http.client.HTTPSConnection("api.zoom.us")
    headers = {
        'authorization': "Bearer " + str(zoomObj.zoom_token),
        'content-type': "application/json"
    }
    conn.request("POST", "/v2/users/" + str(user_id) + "/meetings", generate_request_object(zoomObj), headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data)
    # print(data.decode("utf-8"))

    return data.decode("utf-8")


def generate_request_object(zoomObj):
    myDate = datetime.now()
    #formatedDate = zoomObj.meeting_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    request_body = {
        "topic": zoomObj.meeting_topic,
        "type": 2,
        "start_time": zoomObj.meeting_time,
        "duration": 60,
        "schedule_for": zoomObj.zoom_username,
        "timezone": "Asia/Kolkata",
        "password": zoomObj.zoom_password,
        "agenda": zoomObj.meeting_agenda,
        "settings": {
            "host_video": False,
            "participant_video": False,
            "cn_meeting": False,
            "in_meeting": True,
            "join_before_host": True,
            "mute_upon_entry": False,
            "watermark": False,
            "use_pmi": False,
            "approval_type": 0,
            "registration_type": 1,
            "audio": "both",
            "auto_recording": "local",
            "enforce_login": False,

        }
    }
    print(request_body)

    return json.dumps(request_body)

def sendMail(request, obj):

    messages.add_message(request, messages.INFO, 'Email Successfully Sent')

    recipient_list = [obj.email]
    print(obj.resume)
    print(obj.jd)
    email = EmailMessage(obj.subject, obj.message, obj.from_email, recipient_list)
    email.attach_file('./media/' + str(obj.resume))
    email.attach_file('./media/' + str(obj.jd))
    email.content_subtype = 'html'
    email.send()

    user_recipient_list = [obj.condidate_email]
    email = EmailMessage(obj.subject, obj.message, obj.from_email, user_recipient_list)
    email.attach_file('./media/' + str(obj.jd))
    email.content_subtype = 'html'
    email.send()

    return messages

def sendFeedbackEmail(request,obj):
    messages.add_message(request, messages.INFO, 'Feedback Email Successfully Sent')
    print(obj)
    recipient_list = [obj.email]
    email = EmailMessage(obj.subject, obj.message, obj.from_email, recipient_list)
    email.content_subtype = 'html'
    if str(obj.resume) != None and str(obj.resume) != '':
        email.attach_file('media/' + str(obj.resume))
    if hasattr(obj,'cc_emails'):
        email.cc = obj.cc_emails
    elif hasattr(obj,'cc_email'):
        email.cc = [obj.cc_email]
    email.send()
    return messages

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
   creds = None
   # The file token.pickle stores the user's access and refresh tokens, and is
   # created automatically when the authorization flow completes for the first
   # time.
   if os.path.exists('token.pickle'):
       with open('token.pickle', 'rb') as token:
           creds = pickle.load(token)
   # If there are no (valid) credentials available, let the user log in.
   if not creds or not creds.valid:
       if creds and creds.expired and creds.refresh_token:
           creds.refresh(Request())
       else:
           flow = InstalledAppFlow.from_client_secrets_file(
               CREDENTIALS_FILE, SCOPES)
           creds = flow.run_local_server(port=0)

       # Save the credentials for the next run
       with open('token.pickle', 'wb') as token:
           pickle.dump(creds, token)

   service = build('calendar', 'v3', credentials=creds)
   return service