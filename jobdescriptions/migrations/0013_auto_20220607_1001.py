# Generated by Django 3.1.4 on 2022-06-07 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobdescriptions', '0012_auto_20220606_1053'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jobnotesmodel',
            old_name='job_id',
            new_name='job_idd',
        ),
    ]
