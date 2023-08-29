# Generated by Django 3.1.4 on 2023-02-01 11:21

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('schedulers', '0043_auto_20230201_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='agentcallsdatamodel',
            name='answered_agent_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='agentcallsdatamodel',
            name='id',
            field=models.UUIDField(default=uuid.UUID('be1c2915-e0ea-4d1a-ab49-74faf8908d42'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='sendcleanrequestdatamodel',
            name='id',
            field=models.UUIDField(default=uuid.UUID('972315a2-4652-4852-9cd6-cff00cd20960'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
