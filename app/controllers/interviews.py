from django.shortcuts import render
import json
import datetime
from datetime import timedelta
from django.template.loader import render_to_string
import pytz
from interviews.models import sourceModel
from interviews.serializers import SourceSerializer
from interviews.models import feedbackModel
from interviews.serializers import InterviewsSerializer , InterviewsWriteSerializer
from interviews.models import interviewsModel , ZoomObject , Mails
from interviews.utils import zoom_meeting_create , get_calendar_service , sendMail
from interviews.serializers import FeedbackSerializer , FeedbackWriteSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters , generics
from rest_framework.generics import ListAPIView
from django.db import connection
from comman_utils.utils import handle_file_upload, download_csv
from rest_framework.permissions import DjangoModelPermissions


# Create your views here.
class SourceViewSet(viewsets.ModelViewSet):

    queryset = sourceModel.objects.all()
    serializer_class = SourceSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("source", "created_at")
    search_fields = ('source', 'created_at')
    ordering_fields = ['source' , 'created_at']
    ordering = ['source' , 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        #interviewObj = interviewsModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SourceSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SourceSerializer(self.queryset, many=True)
        return Response(serializer.data)


    def create(self, request):
        serializeObj = SourceSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return sourceModel.objects.get(pk=pk)
        except sourceModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = SourceSerializer(candObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = SourceSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class InterviewViewSet(viewsets.ModelViewSet):

    queryset = interviewsModel.objects.all()
    serializer_class = InterviewsSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("candidate_name__first_name", 'time_slot__time_slot','interviewer_name__first_name' , "created_at")
    search_fields = ("candidate_name__first_name", 'time_slot__time_slot','interviewer_name__first_name' , "created_at")
    ordering_fields = ['candidate_name__first_name' ,'time_slot__time_slot' ,'interviewer_name__first_name','created_at']
    ordering = ['candidate_name__first_name' ,'time_slot__time_slot' ,'interviewer_name__first_name','created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        #interviewObj = interviewsModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = InterviewsSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = InterviewsSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = InterviewsWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            print(request.data)
            print(serializeObj.validated_data)
            interviewer_id = str(request.data['interviewer_name']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            candidate_id = str(request.data['candidate_name']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            jd_id = str(request.data['jd_attachment']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            time_slot_id = str(request.data['time_slot']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            if interviewsModel.objects.filter(interviewer_name_id=interviewer_id,
                                              time_slot_id=time_slot_id,
                                              meeting_time=request.data['meeting_time']).count() == 0:
                serializeObj.save(updated_by_id = request.user.id , created_by_id = request.user.id)
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT first_name, primary_email, primary_phone_number, resume ,last_name FROM osms_candidates where id=%s",
                    [candidate_id])
                condidate = cursor.fetchone()
                print(type(condidate))
                print(condidate[1])
                condidate_resume = condidate[3]
                print(condidate_resume)

                cursor.execute("SELECT first_name, primary_email, zoom_username, zoom_password,"
                               "zoom_api_key, zoom_api_secret, zoom_token FROM osms_interviewers where id=%s",
                               [interviewer_id])
                interviewer = cursor.fetchone()
                print(interviewer)
                print(interviewer[1])

                cursor.execute("SELECT job_title, job_pdf FROM osms_job_description where id=%s",
                               [jd_id])
                jds = cursor.fetchone()
                cursor.execute("SELECT time_slot FROM interviewers_time_slots where id=%s",
                               [time_slot_id])
                time_slot = cursor.fetchone()
                print(jds)
                print(jds[1])

                zoomObj = ZoomObject()
                zoomObj.zoom_username = interviewer[2]
                zoomObj.zoom_password = interviewer[3]
                zoomObj.zoom_api_key = interviewer[4]
                zoomObj.zoom_api_secret = interviewer[5]
                zoomObj.zoom_token = interviewer[6]
                zoomObj.meeting_topic = jds[0]
                zoomObj.meeting_agenda = serializeObj.data['remarks']
                zoomObj.meeting_time = serializeObj.data['meeting_time']
                zoomObj.meeting_time_zone = serializeObj.data['time_zone']

                print(zoomObj)

                api_res = zoom_meeting_create(zoomObj)
                api = json.loads(api_res)
                print(api)
                print(request.user.email)
                formatedDate = serializeObj.data['meeting_time']

                interview_title = 'Invitation: Video Interview - ' + str(condidate[0]) +' '+str(condidate[4])+ ' - ' + str(jds[0])
                context = {
                    'zoomInfo': api,
                    'candidateName': condidate[0],
                    'candidateEmail': condidate[1],
                    'candidatePhoe': condidate[2],
                    'interviewerName': interviewer[0],
                    'interviewerEmail': interviewer[1],
                    'condidate_resume': condidate_resume,
                    'interview_title': interview_title,
                    'loggedin_user_email': request.user.email,
                    'loggedin_user_name': request.user.first_name + ' ' + request.user.last_name
                }

                mail = Mails()
                mail.subject = interview_title
                mail.from_email = request.user.email
                mail.email = interviewer[1]
                mail.message = render_to_string('email.html', context)
                mail.resume = condidate_resume
                mail.condidate_email = condidate[1]
                mail.jd = jds[1]
                mail_res = sendMail(request, mail)
                print(mail_res)
                """start_datetime = datetime.datetime.now(tz=pytz.utc)
                try:
                    service = get_calendar_service()
                    start = start_datetime.isoformat()
                    end = (start_datetime + timedelta(hours=1)).isoformat()
                    event_result = service.events().insert(calendarId='primary',
                                                           body={
                                                               "summary": interview_title,
                                                               "description": "Opallios is inviting you to a scheduled zoom meeting \n Join Zoom Meeting on : \n" +
                                                                              api['join_url'] +
                                                                              "\nMeeting ID : " + str(
                                                                   api['id']) + "\nPassword  : " + str(api['password']),
                                                               "start": {"dateTime": start, "timeZone": 'Asia/Kolkata'},
                                                               "end": {"dateTime": end, "timeZone": 'Asia/Kolkata'},
                                                               "attendees": [{
                                                                   "email": condidate[1],
                                                                   "displayName": condidate[0]
                                                               },
                                                                   {
                                                                       "email": interviewer[1],
                                                                       "displayName": interviewer[0]
                                                                   }
                                                               ]
                                                           }
                                                           ).execute()

                    print("created event")
                    print("id: ", event_result['id'])
                    print("summary: ", event_result['summary'])
                    print("starts at: ", event_result['start']['dateTime'])
                    print("ends at: ", event_result['end']['dateTime'])
                    print("ends at: ", event_result['attendees'])

                except Exception as e:
                    print(e)
                    print('Something goes Wrong=======')"""
                return Response(serializeObj.data, status=status.HTTP_201_CREATED)
            else:
                return Response(data = {'details':'Interviewer is already booked for given slot'} ,status=status.HTTP_400_BAD_REQUEST)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return interviewsModel.objects.get(pk=pk)
        except interviewsModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = InterviewsWriteSerializer(candObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = InterviewsWriteSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            print(request.data)
            print(serializeObj.validated_data)
            interviewer_id = str(request.data['interviewer_name']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            candidate_id = str(request.data['candidate_name']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            jd_id = str(request.data['jd_attachment']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            time_slot_id = str(request.data['time_slot']).replace('UUID', ''). \
                replace('(\'', '').replace('\')', '').replace('-', '')
            if interviewsModel.objects.filter(interviewer_name_id=interviewer_id,
                                              time_slot_id=time_slot_id,
                                              meeting_time=request.data['meeting_time']).count() == 0:
                serializeObj.save(updated_by_id = request.user.id , status = 'Rescheduled')
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT first_name, primary_email, primary_phone_number, resume FROM osms_candidates where id=%s",
                    [candidate_id])
                condidate = cursor.fetchone()
                print(type(condidate))
                print(condidate[1])
                condidate_resume = condidate[3]
                print(condidate_resume)

                cursor.execute("SELECT first_name, primary_email, zoom_username, zoom_password,"
                               "zoom_api_key, zoom_api_secret, zoom_token FROM osms_interviewers where id=%s",
                               [interviewer_id])
                interviewer = cursor.fetchone()
                print(interviewer)
                print(interviewer[1])

                cursor.execute("SELECT job_title, job_pdf FROM osms_job_description where id=%s",
                               [jd_id])
                jds = cursor.fetchone()
                cursor.execute("SELECT time_slot FROM interviewers_time_slots where id=%s",
                               [time_slot_id])
                time_slot = cursor.fetchone()
                print(jds)
                print(jds[1])

                zoomObj = ZoomObject()
                zoomObj.zoom_username = interviewer[2]
                zoomObj.zoom_password = interviewer[3]
                zoomObj.zoom_api_key = interviewer[4]
                zoomObj.zoom_api_secret = interviewer[5]
                zoomObj.zoom_token = interviewer[6]
                zoomObj.meeting_topic = jds[0]
                zoomObj.meeting_agenda = serializeObj.data['remarks']
                zoomObj.meeting_time = serializeObj.data['meeting_time']
                zoomObj.meeting_time_zone = serializeObj.data['time_zone']

                print(zoomObj)

                api_res = zoom_meeting_create(zoomObj)
                api = json.loads(api_res)
                print(api)
                print(request.user.email)
                formatedDate = serializeObj.data['meeting_time']

                interview_title = 'Invitation: Video Interview - ' + str(condidate[0]) + ' - ' + str(
                    jds[0]) + ' @ ' + str(formatedDate) + ' (' + str(serializeObj.data['time_zone']) + ') (' + str(
                    interviewer[1]) + ')'
                context = {
                    'zoomInfo': api,
                    'candidateName': condidate[0],
                    'candidateEmail': condidate[1],
                    'candidatePhoe': condidate[2],
                    'interviewerName': interviewer[0],
                    'interviewerEmail': interviewer[1],
                    'condidate_resume': condidate_resume,
                    'interview_title': interview_title,
                    'loggedin_user_email': request.user.email,
                    'loggedin_user_name': request.user.first_name + ' ' + request.user.last_name
                }

                mail = Mails()
                mail.subject = interview_title
                mail.from_email = request.user.email
                mail.email = interviewer[1]
                mail.message = render_to_string('email.html', context)
                mail.resume = condidate_resume
                mail.condidate_email = condidate[1]
                mail.jd = jds[1]
                mail_res = sendMail(request, mail)
                print(mail_res)
                """start_datetime = datetime.datetime.now(tz=pytz.utc)
                try:
                    service = get_calendar_service()
                    start = start_datetime.isoformat()
                    end = (start_datetime + timedelta(hours=1)).isoformat()
                    event_result = service.events().insert(calendarId='primary',
                                                           body={
                                                               "summary": interview_title,
                                                               "description": "Opallios is inviting you to a scheduled zoom meeting \n Join Zoom Meeting on : \n" +
                                                                              api['join_url'] +
                                                                              "\nMeeting ID : " + str(
                                                                   api['id']) + "\nPassword  : " + str(api['password']),
                                                               "start": {"dateTime": start, "timeZone": 'Asia/Kolkata'},
                                                               "end": {"dateTime": end, "timeZone": 'Asia/Kolkata'},
                                                               "attendees": [{
                                                                   "email": condidate[1],
                                                                   "displayName": condidate[0]
                                                               },
                                                                   {
                                                                       "email": interviewer[1],
                                                                       "displayName": interviewer[0]
                                                                   }
                                                               ]
                                                           }
                                                           ).execute()

                    print("created event")
                    print("id: ", event_result['id'])
                    print("summary: ", event_result['summary'])
                    print("starts at: ", event_result['start']['dateTime'])
                    print("ends at: ", event_result['end']['dateTime'])
                    print("ends at: ", event_result['attendees'])

                except Exception as e:
                    print(e)
                    print('Something goes Wrong=======')"""
                return Response(serializeObj.data, status=status.HTTP_201_CREATED)
            else:
                return Response(data = {'details':'Interviewer is already booked for given slot'} ,status=status.HTTP_400_BAD_REQUEST)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FeedbackViewSet(viewsets.ModelViewSet):

    queryset = feedbackModel.objects.all()
    serializer_class = FeedbackSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("candidate_name__first_name", 'forwarded' , "created_at")
    search_fields = ("candidate_name__first_name",'forwarded' ,"created_at")
    ordering_fields = ['candidate_name__first_name' , 'created_at']
    ordering = ['candidate_name__first_name' , 'created_at']
    permission_classes = [DjangoModelPermissions]

    def list(self, request):
        #feedbackObj = feedbackModel.objects.all()
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FeedbackSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = FeedbackSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = FeedbackWriteSerializer(data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(created_by_id = request.user.id , updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return feedbackModel.objects.get(pk=pk)
        except feedbackModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = FeedbackWriteSerializer(candObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = FeedbackWriteSerializer(candObj, data=request.data)
        if serializeObj.is_valid():
            serializeObj.save(updated_by_id = request.user.id)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        candObj = self.get_object(pk)
        candObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class ExportInterviewsModel(generics.ListAPIView):

    def get(self, request, format=None):
        response = download_csv(interviewsModel, request, interviewsModel.objects.all())
        return response