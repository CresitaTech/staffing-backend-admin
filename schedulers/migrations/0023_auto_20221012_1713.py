# Generated by Django 3.1.4 on 2022-10-12 17:13

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('schedulers', '0022_auto_20220927_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendcleanrequestdatamodel',
            name='id',
            field=models.UUIDField(default=uuid.UUID('f78f1f7b-c2b2-4d71-94db-1e57cb89395c'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
