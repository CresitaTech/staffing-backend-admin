# Generated by Django 3.1.4 on 2022-11-15 10:40

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('schedulers', '0030_auto_20221114_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendcleanrequestdatamodel',
            name='id',
            field=models.UUIDField(default=uuid.UUID('32945937-193b-46b0-b9a9-0c5155dd716b'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
