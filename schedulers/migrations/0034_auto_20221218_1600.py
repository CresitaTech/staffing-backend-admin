# Generated by Django 3.1.4 on 2022-12-18 16:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('schedulers', '0033_auto_20221218_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendcleanrequestdatamodel',
            name='id',
            field=models.UUIDField(default=uuid.UUID('0a377a35-b0be-4b1a-a321-10b08c243dae'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
