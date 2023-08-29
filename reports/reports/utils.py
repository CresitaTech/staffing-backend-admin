from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from html2docx import html2docx
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.contrib import messages
from weasyprint import HTML

from staffingapp.settings import EMAIL_FROM_USER



"""
Method for sending jd mail on submission
"""

def sendJDMail(request, obj):
    messages.add_message(request, messages.INFO, 'JD Email Successfully Sent')
    print(obj)
    recipient_list = [obj.email]
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=obj.from_email,
                         to=recipient_list)
    email.content_subtype = 'html'
    if str(obj.resume) != None and str(obj.resume) != '':
        email.attach_file('.'+str(obj.resume))
    email.cc = [obj.cc_email.strip()]
    email.send()
    return messages


def sortDic(data):
    sorteddic = sorted(data, key=lambda x: x['rank'], reverse=True)
    return sorteddic
