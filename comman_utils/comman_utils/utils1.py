import csv
import os

from django.http import HttpResponse


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

