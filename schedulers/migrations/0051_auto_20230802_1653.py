# Generated by Django 3.1.4 on 2023-08-02 16:53

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('schedulers', '0050_auto_20230801_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendcleanrequestdatamodel',
            name='id',
            field=models.UUIDField(default=uuid.UUID('b063c7ae-f0eb-4534-b422-697dcbaaf42c'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
