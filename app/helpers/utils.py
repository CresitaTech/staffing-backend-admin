import csv
import os
from email.mime.image import MIMEImage

from dateutil.relativedelta import relativedelta
from datetime import date
from datetime import datetime

import datetime as delta

from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.conf import settings

from staffingapp.settings import EMAIL_HOST
from vendors.models import emailConfigurationModel
from vendors.serializers import EmailConfigurationSerializer
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def handle_file_upload(f, path):
    path = os.path.join('media/' + path, f.name)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def download_csv(modeladmin, request, queryset):
    opts = queryset.model._meta
    model = queryset.model
    response = HttpResponse(content_type='text/csv')

    # force download.
    response['Content-Disposition'] = 'attachment; filename="export-candidate-data.csv"'

    # the csv writer
    writer = csv.writer(response)
    field_names = [field.name for field in opts.fields]
    # Write a first row with header information
    writer.writerow(field_names)
    # Write data rows
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response


def get_current_datetime():
    now = datetime.now()
    full = "%Y-%m-%d %H:%M:%S.%f"
    myfmt = "%Y-%m-%d %H:%M:%S"
    current_datetime = datetime.strptime(str(now), full).strftime(myfmt)
    return current_datetime


def get_current_date():
    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d")
    return current_datetime


def yesterday_datetime():
    today = date.today()
    days = delta.timedelta(1)
    yesterday_date = today - days
    return yesterday_date


def get_last_saturday():
    today = date.today()
    sat_offset = (today.weekday() - 12) % 7
    saturday_date = today - delta.timedelta(days=sat_offset)
    full = "%Y-%m-%d %H:%M:%S.%f"
    myfmt = "%Y-%m-%d %H:%M:%S"
    #saturday = datetime.strptime(str(saturday_date), full).strftime(myfmt)
    return saturday_date


def week_date_range():
    today = date.today()
    #start = today - datetime.timedelta(days=today.weekday())
    #end = start + datetime.timedelta(days=6)
    start = today - delta.timedelta(days=6)
    end = today
    
    return start, end
    

def month_date_range():
    today = date.today()
    # first_day_this_month = date(day=1, month=today.month, year=today.year)
    # last_day_last_month = first_day_this_month - relativedelta(days=1)
    
    #first_day_this_month = date(day=1, month=today.month, year=today.year)
    #last_day_last_month = last_day_of_month(datetime.date(today.year, today.month, 1))
    
    first_day_this_month = today - delta.timedelta(days=30)
    last_day_last_month = today

    return first_day_this_month, last_day_last_month


def last_day_of_month(any_day):
    # this will never fail
    # get close to the end of the month for any day, and add 4 days 'over'
    next_month = any_day.replace(day=28) + delta.timedelta(days=4)
    # subtract the number of remaining 'overage' days to get last day of current month, or said programattically said, the previous day of the first of next month
    return next_month - delta.timedelta(days=next_month.day)


def get_mail_object(self, request):
    messages.add_message(request, messages.INFO, 'Mail Successfully Configured')

    mailObj = emailConfigurationModel.objects.filter(created_by_id=request.user.id)
    mailSer = EmailConfigurationSerializer(mailObj, many=True)
    if mailSer.data[0] is None:
        return None;
    rows = dict(mailSer.data[0])
    server = smtplib.SMTP(rows['host_name'] + ':' + rows['port'])
    server.starttls()
    server.login(rows['email'], rows['password'])
    return server, rows