# Generated by Django 3.1.4 on 2022-08-26 12:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('schedulers', '0002_sendcleandatamodel_sendcleanrequestdatamodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='sendcleanrequestdatamodel',
            name='id',
            field=models.UUIDField(default=uuid.UUID('3dcf375d-0443-40de-9cae-09d3f8c1d729'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='sendcleandatamodel',
            name='id',
            field=models.UUIDField(default=uuid.UUID('dfa92b3f-8a44-44ab-927a-4b8cd47e8984'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='sendcleanrequestdatamodel',
            name='_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
