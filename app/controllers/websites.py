from django.shortcuts import render

# Create your views here.
from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from candidates.models import Candidates
from candidates.serializers import CandidateSerializer, CandidateWriteSerializer
from jobdescriptions.models import jobModel
from jobdescriptions.serializers import JobDescriptionSerializer
from website.serializers import CandidateWebsiteSerializer, JobWebsiteSerializer, PostalRequestSerializer
from interviews.models import Mails
from django.template.loader import render_to_string
from django.core.mail import  EmailMessage
from vendors.models import MailEventsModel

class WebsiteCandidatesViewSet(viewsets.ModelViewSet):
    queryset = Candidates.objects.none()
    serializer_class = CandidateSerializer
    permission_classes = [AllowAny]

    def list(self, request):
        queryset = Candidates.objects.all().order_by('-id')[:10]
        serializer = CandidateSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = CandidateWebsiteSerializer(data=request.data)
        if serializeObj.is_valid():
            print(serializeObj.validated_data)
            context = {
                "client_name": serializeObj.validated_data['client_name'],
                "client_phone": serializeObj.validated_data['client_phone'],
                "client_email": serializeObj.validated_data['client_email'],
                "client_message": serializeObj.validated_data['client_message'],
                "candidate_resume_downloaded":serializeObj.validated_data['candidate_name']
                }
            mail = Mails()
            mail.subject = "New Client Applied"
            mail.from_email = "osms.opallios@gmail.com"
            mail.email = 'agrawalv@cresitatech.com'
            mail.message = render_to_string('apply_client.html', context)
            send_mail(request,mail)
            #serializeObj.save()
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            # obj = Candidates.objects.get(pk=pk)
            obj = Candidates.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except Candidates.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = CandidateWriteSerializer(candObj)
        return Response(serializeObj.data)


class WebsiteJobsViewSet(viewsets.ModelViewSet):
    queryset = jobModel.objects.none()
    serializer_class = JobDescriptionSerializer
    permission_classes = [AllowAny]

    def list(self, request):
        queryset = jobModel.objects.all().order_by('-id')[:10]
        serializer = JobDescriptionSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializeObj = JobWebsiteSerializer(data=request.data)
        if serializeObj.is_valid():
            print(serializeObj.validated_data)
            context = {
                "first_name": serializeObj.validated_data['first_name'],
                "last_name": serializeObj.validated_data['last_name'],
                "date_of_birth": serializeObj.validated_data['date_of_birth'],
                "job_title": serializeObj.validated_data['job_title'],
                "qualification": serializeObj.validated_data['qualification'],
                "primary_email": serializeObj.validated_data['primary_email'],
                "secondary_email": serializeObj.validated_data['secondary_email'],
                "primary_phone_number": serializeObj.validated_data['primary_phone_number'],
                "secondary_phone_number": serializeObj.validated_data['secondary_phone_number'],
                "designation": serializeObj.validated_data['designation'],
                "salary_Rate": serializeObj.validated_data['salary_Rate'],
                "visa": serializeObj.validated_data['visa'],
                "company_name": serializeObj.validated_data['company_name'],
                "total_experience": serializeObj.validated_data['total_experience'],
                "total_exp_usa": serializeObj.validated_data['total_exp_usa'],
                "any_offer_in_hand": serializeObj.validated_data['any_offer_in_hand'],
                "current_location": serializeObj.validated_data['current_location'],
                "skills1": serializeObj.validated_data['skills1'],
                "skills2": serializeObj.validated_data['skills2'],
                "remarks": serializeObj.validated_data['remarks'],
                }
            mail = Mails()
            mail.subject = "New Candidate Applied for job"
            mail.from_email = "osms.opallios@gmail.com"
            mail.email = 'agrawalv@cresitatech.com'
            mail.message = render_to_string('apply_candidate.html', context)
            mail.jd = serializeObj.validated_data['resume']
            send_job_mail(request,mail)
            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            # obj = Candidates.objects.get(pk=pk)
            obj = jobModel.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except jobModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = JobDescriptionSerializer(candObj)
        return Response(serializeObj.data)

def send_mail(request,obj):
    recipient_list = [obj.email]
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=obj.from_email, to=recipient_list)
    email.content_subtype = 'html'
    email.send()
    
def send_job_mail(request,obj):
    recipient_list = [obj.email]
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=obj.from_email, to=recipient_list)
    email.content_subtype = 'html'
    email.attach(obj.jd.name, obj.jd.read(), obj.jd.content_type)
    email.send()


class PostalRequestHandler(viewsets.ModelViewSet):
    queryset = MailEventsModel.objects.none()
    serializer_class = PostalRequestSerializer

    permission_classes = [AllowAny]

    def list(self, request):
        queryset = MailEventsModel.objects.all().order_by('-id')[:10]
        serializer = PostalRequestSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        if request.data is not None and request.data != '':
            MailEventsModel.objects.create(maildata=request.data)
            return Response(data={'msg': "Success"}, status=status.HTTP_201_CREATED)
        return Response(data={'msg': "Fail"}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            # obj = Candidates.objects.get(pk=pk)
            obj = MailEventsModel.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except MailEventsModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk):
        candObj = self.get_object(pk)
        serializeObj = PostalRequestSerializer(candObj)
        return Response(serializeObj.data)
