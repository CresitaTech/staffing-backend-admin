# Generated by Django 3.1.4 on 2022-06-01 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0018_auto_20220401_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidatestagemodel',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Admin'), (9, 'BDM MANAGER'), (2, 'Recruiter Manager'), (3, 'Recruiter')], default=3, null=True),
        ),
    ]
