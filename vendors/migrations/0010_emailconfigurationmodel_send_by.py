# Generated by Django 3.1.4 on 2021-09-15 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0009_auto_20210913_1030'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailconfigurationmodel',
            name='send_by',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
