# Generated by Django 3.1.4 on 2022-10-12 17:20

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('schedulers', '0028_auto_20221012_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendcleanrequestdatamodel',
            name='id',
            field=models.UUIDField(default=uuid.UUID('6be5210d-cd0f-4330-aa0d-a4bda3c2d07d'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
