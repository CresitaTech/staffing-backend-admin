# Generated by Django 3.1.4 on 2021-11-30 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0015_auto_20211130_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidatesjobdescription',
            name='send_out_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='candidatesjobdescription',
            name='submission_date',
            field=models.DateTimeField(null=True),
        ),
    ]
