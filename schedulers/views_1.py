from django.shortcuts import render
import csv
import os
from users.models import Countries  # imports the model


def index(request):
    print("Empty view")
    with open('countries.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            p = Countries(country_code=row['country_code'], country_name=row['country_name'])
            p.save()
    print("File successfully uploaded")

    return render(request, "File successfully uploaded")

