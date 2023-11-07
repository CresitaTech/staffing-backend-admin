from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from html2docx import html2docx
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.contrib import messages


from datetime import datetime
import pytz
from pytz import timezone
import logging
from staffingapp.settings import EMAIL_FROM_USER
logger = logging.getLogger(__name__)


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    """html_to = HTML(string=html)
    result = html_to.write_pdf()
    return HttpResponse(result, content_type='application/pdf')"""
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1", 'ignore')), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def convert_to_doc(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)

    buf = html2docx(html, title="My Document")
    print(buf)
    return buf


def sendAssingmentMail(request, obj):
    messages.add_message(request, messages.INFO, 'Assingment Email Successfully Sent')
    print(obj)
    recipient_list = [obj.email]
    print(obj.from_email)
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=EMAIL_FROM_USER, to=recipient_list)
    email.content_subtype = 'html'
    if obj.jd != None and str(obj.jd) != '':
        email.attach_file('media/' + str(obj.jd))
    email.cc = obj.cc_email
    email.send()
    return messages


def sendJobNotesMail(request, obj):
    messages.add_message(request, messages.INFO, 'Job Notes Successfully Sent')
    print(obj)
    recipient_list = [obj.email]
    print(obj.from_email)
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=EMAIL_FROM_USER, to=recipient_list)
    email.content_subtype = 'html'
    if obj.jd != None and str(obj.jd) != '':
        email.attach_file('media/' + str(obj.jd))
    # email.cc = obj.cc_email
    email.send()
    return messages


"""
Method for sending jd mail on submission
"""


def sendJDMail(request, obj):
    messages.add_message(request, messages.INFO, 'JD Email Successfully Sent')
    print(obj)
    recipient_list = [obj.email]
    email = EmailMessage(subject=obj.subject, body=obj.message, from_email=EMAIL_FROM_USER,
                         to=recipient_list)
    email.content_subtype = 'html'
    if str(obj.resume) != None and str(obj.resume) != '':
        email.attach_file('.' + str(obj.resume))
    email.cc = [obj.cc_email.strip()]
    email.send()
    return messages


"""
Method for sending jd mail on submission
"""

"""def sendJDMail(request, obj):
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
    return messages"""


def counvert_ist_to_pst(userCountry, recruiterCountry):
    format = "%Y-%m-%d %H:%M:%S"
    current_datetime = datetime.now()
    logger.info("current_datetime1: " + str(current_datetime))
    datetime_str = str(current_datetime).split(".")[0]
    current_datetime = datetime.strptime(datetime_str, format)
    if userCountry == 'US':
        current_datetime = current_datetime.astimezone(timezone('US/Pacific'))
        datetime_str = str(current_datetime)[:19]
        current_datetime = datetime.strptime(datetime_str, format)
        logger.info("bdm current_datetime2: " + str(current_datetime))

    if userCountry == 'Both':
        if recruiterCountry == "US":
            current_datetime = current_datetime.astimezone(timezone('US/Pacific'))
            datetime_str = str(current_datetime)[:19]
            current_datetime = datetime.strptime(datetime_str, format)
            logger.info("recruiter current_datetime2: " + str(current_datetime))

    return current_datetime
