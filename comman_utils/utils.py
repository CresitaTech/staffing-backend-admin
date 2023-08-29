import csv
import os
from email.mime.image import MIMEImage

from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
from datetime import datetime, time, timedelta

import datetime as delta

from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.conf import settings
from django.http import StreamingHttpResponse

from staffingapp.settings import EMAIL_HOST
from vendors.models import emailConfigurationModel
from vendors.serializers import EmailConfigurationSerializer
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_datetime_from_date(end_date):
    end_date = end_date + ' 23:59:59'
    return end_date


def get_startdate_and_enddate(start_date, end_date):
    start_date = start_date + ' 00:00:00'
    end_date = end_date + ' 23:59:59'
    return start_date, end_date


def get_current_day_start_and_end_datetime():
    today = datetime.now()
    # start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    # end = start + timedelta(1)
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)
    return start, end


def get_weekly_report_start_and_end_datetime(country):
    today = datetime.now()
    start_date = today - timedelta(days=8)
    if country == 'US':
        start_date = today - timedelta(days=8)
    start = datetime.combine(start_date, time.min)
    end = datetime.combine(today, time.max)
    return start, end


def get_start_and_end_datetime_before_twenty_four_hours_days(country):
    today = datetime.now()
    start_date = today - timedelta(days=2)
    if country == 'US':
        start_date = today - timedelta(days=3)
    start = datetime.combine(start_date, time.min)
    end = datetime.combine(today, time.max)
    return start, end


def get_daily_report_start_and_end_datetime(country):
    today = datetime.now()
    # current_datetime = now.strftime("%Y-%m-%d")
    if country == 'US':
        today = today - timedelta(days=1)
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)
    return start, end


def handle_file_upload(f, path):
    path = os.path.join('media/' + path, f.name)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


class CSVBuffer(object):
    def write(self, value):
        return value


def iter_items(items, pseudo_buffer, field_names):
    writer = csv.DictWriter(pseudo_buffer, fieldnames=field_names)
    yield pseudo_buffer.write(field_names)

    for obj in items:
        yield writer.writerow([getattr(obj, field) for field in field_names])


def download_csv(modeladmin, request, queryset):
    opts = queryset.model._meta
    model = queryset.model
    ERROR_503 = 'something went wrong.'
    response = None
    """response = HttpResponse(content_type='text/csv')
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
    return response"""
    field_names = [field.name for field in opts.fields]

    csv_buffer = CSVBuffer()
    csv_writer = csv.writer(csv_buffer)
    rows = (csv_writer.writerow(row) for row in queryset)
    # (iter_items(rows, CSVBuffer(), field_names))
    response = StreamingHttpResponse(streaming_content=rows,
                                     content_type='text/csv', )
    file_name = 'export-candidate-data'
    response['Content-Disposition'] = 'attachment;filename=%s.csv' % (file_name)
    logger.info("File starting to download.......")

    """    try:
        csv_buffer = CSVBuffer()
        csv_writer = csv.writer(csv_buffer)
        rows = (csv_writer.writerow(row) for row in queryset)
        # (iter_items(rows, CSVBuffer(), field_names))
        response = StreamingHttpResponse(streaming_content=rows,
                                         content_type='text/csv', )
        file_name = 'export-candidate-data'
        response['Content-Disposition'] = 'attachment;filename=%s.csv' % (file_name)
        logger.info("File starting to download.......")
    except Exception as e:
        logger.info("Error Found: " + str(e))
        messages.error(request, ERROR_503)
        # return redirect(DASHBOARD_URL)"""

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

    return str(first_day_this_month) + " 00:00:00", str(last_day_last_month) + " 23:59:59"


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


def get_number_of_days(end_date, start_date):
    numberOfDays = (datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').date() - datetime.strptime(start_date,
                                                                                                         '%Y-%m-%d').date()).days
    return numberOfDays