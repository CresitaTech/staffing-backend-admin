# Create your views here.
from django.shortcuts import render
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from django.core.files import File
from io import BytesIO

from interviews.models import Mails
from jobdescriptions.utils import render_to_pdf
from offerletters.filters import OfferLettersFilter
from offerletters.models import OfferLettersModel
from offerletters.serializers import OfferLettersSerializer
from users.models import User
from users.serializers import UserSerializer
import logging
from rest_framework import status
from django.core.mail import EmailMessage
from django.contrib import messages

logger = logging.getLogger(__name__)


def showOfferMail(request):
    output = []
    return render(request, "offer_letter_email.html", {'data': output})


class OfferLetters(viewsets.ModelViewSet):
    queryset = OfferLettersModel.objects.none()
    serializer_class = OfferLettersSerializer
    # permission_classes = [DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, ]  # SearchFilter,
    ordering_fields = ['candidate_name', 'contact_no', 'created_at']
    ordering = ['candidate_name', 'contact_no', 'created_at']
    filter_fields = ["candidate_name", "contact_no", "created_at"]
    search_fields = ['candidate_name', 'contact_no', 'created_at']
    filter_class = OfferLettersFilter

    def list(self, request):
        offerLetterObj = User.objects.get(pk=request.user.id)
        serializeObj = UserSerializer(offerLetterObj)
        # print(serializeObj.data)
        groups = dict(serializeObj.data)
        # print(groups)
        # print(len(groups))
        userGroupDict = None
        userGroup = None
        if len(groups['groups']) > 0:
            # print(groups['groups'])
            # print(groups['groups'][0])
            # userGroupDict = None
            userGroupDict = dict(groups['groups'][0])
        if userGroupDict is not None:
            userGroup = userGroupDict['name']
        print(userGroup)
        logger.info('userGroup Data: %s' % userGroup)
        if userGroup is not None and userGroup == 'ADMIN':
            queryset = OfferLettersModel.objects.all()
        elif userGroup is not None and userGroup == 'BDM MANAGER':
            queryset = OfferLettersModel.objects.filter(created_by_id=request.user.id)
            # print(str(queryset.query))
        elif userGroup is not None and userGroup == 'RECRUITER MANAGER':
            queryset = OfferLettersModel.objects.all()
            # queryset = clientModel.objects.filter(
            #   Q(created_by_id__created_by_id=request.user.id) | Q(created_by_id=request.user.id))
            # print(str(queryset.query))
        elif userGroup is not None and userGroup == 'RECRUITER':
            queryset = OfferLettersModel.objects.none()
            # queryset = clientModel.objects.filter(created_by_id=request.user.id)
            # print(str(queryset.query))
        else:
            queryset = OfferLettersModel.objects.none()

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OfferLettersSerializer(page, many=True)
            # serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = OfferLettersSerializer(self.queryset, many=True)
        logger.info('OfferLetter List: ' + str(serializer.data))
        return Response(serializer.data)

    def create(self, request):
        logger.info('New OfferLetter Create data: ' + str(request.data))
        serializeObj = OfferLettersSerializer(data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save(created_by_id=request.user.id, updated_by_id=request.user.id)
            context = {'instance': serializeObj.validated_data}
            pdf = render_to_pdf('offer_letter_email.html', context)

            candidate_name = str(obj.candidate_name).replace('\\', '_').replace(r'/', '_')

            filename = str(obj.id) + '-' + str(candidate_name) + ".pdf"
            serializeObj.save(offer_letter_pdf=File(name=filename, file=BytesIO(pdf.content)),
                              created_by_id=request.user.id, updated_by_id=request.user.id)
            logger.info('Offer Letter Pdf Saved Successfully: ' + str(serializeObj.data))

            mail = Mails()
            mail.from_email = 'osms.opallios@gmail.com'
            mail.email = request.user.email
            mail.subject = 'New Offer Letter submissions for HR '
            mail.resume = serializeObj.data['offer_letter_pdf']
            mail.jd = serializeObj.data['resume']
            mail.message = render_to_string('offer_letter_email.html', context)
            mail.condidate_email = None
            # setattr(mail, 'cc_email', ['kuriwaln@opallios.com', 'agrawalv@cresitatech.com'])
            sendOfferLetterMail(request, mail)
            logger.info('Mail Send Successfully' + str(mail))

            return Response(serializeObj.data, status=status.HTTP_201_CREATED)
        logger.error('OfferLetter Post Serialized Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return OfferLettersModel.objects.get(pk=pk)
        except OfferLettersModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        offerLetterObj = self.get_object(pk)
        serializeObj = OfferLettersSerializer(offerLetterObj)
        return Response(serializeObj.data)

    def update(self, request, pk):
        logger.info('Update OfferLetter Data: ' + str(request.data))
        offerLetterObj = self.get_object(pk)
        serializeObj = OfferLettersSerializer(offerLetterObj, data=request.data)
        if serializeObj.is_valid():
            obj = serializeObj.save(updated_by_id=request.user.id)

            context = {'instance': serializeObj.validated_data}
            pdf = render_to_pdf('offer_letter_email.html', context)

            candidate_name = str(obj.candidate_name).replace('\\', '_').replace(r'/', '_')

            filename = str(obj.id) + '-' + str(candidate_name) + ".pdf"
            serializeObj.save(offer_letter_pdf=File(name=filename, file=BytesIO(pdf.content)),
                              created_by_id=request.user.id, updated_by_id=request.user.id)
            logger.info('Offer Letter Pdf Saved Successfully: ' + str(serializeObj.data))

            mail = Mails()
            mail.from_email = 'osms.opallios@gmail.com'
            mail.email = request.user.email
            mail.subject = 'Update Offer Letter submissions for HR '
            mail.resume = serializeObj.data['offer_letter_pdf']
            mail.jd = serializeObj.data['resume']
            mail.message = render_to_string('offer_letter_email.html', context)
            mail.condidate_email = None
            # setattr(mail, 'cc_email', ['kuriwaln@opallios.com', 'agrawalv@cresitatech.com'])
            sendOfferLetterMail(request, mail)
            logger.info('Mail Send Successfully' + str(mail))


            # sendOfferLetterMail(serializeObj.data)
            return Response(serializeObj.data, status=status.HTTP_200_OK)
        logger.error('OfferLetter Update Serialized Error: ' + str(serializeObj.errors))
        return Response(serializeObj.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        offerLetterObj = self.get_object(pk)
        offerLetterObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def sendOfferLetterMail(request, obj):
    messages.add_message(request, messages.INFO, 'Offer Letter Email Successfully Sent')
    recipient_list = [obj.email]
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=obj.from_email,
                         to=recipient_list)
    email.content_subtype = 'html'
    if str(obj.resume) != None and str(obj.resume) != '':
        email.attach_file('.'+str(obj.resume))
    if str(obj.jd) != None and str(obj.jd) != '':
        email.attach_file('.'+str(obj.jd))
    email.cc = ['minglaniy@opallios.com', 'hr@cresitatech.com', 'kuriwaln@opallios.com']
    email.send()
    # 'paradkaro@opallios.com',
    return messages
