# Generated by Django 3.1.4 on 2023-01-11 17:41

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('schedulers', '0039_auto_20230109_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendcleanrequestdatamodel',
            name='id',
            field=models.UUIDField(default=uuid.UUID('977e1edb-32cb-416b-bdc3-cfa3c19a52a3'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
