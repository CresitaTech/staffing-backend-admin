# Generated by Django 3.1.4 on 2021-01-19 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobdescriptions', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jobmodel',
            old_name='revenue_frequqney',
            new_name='revenue_frequency',
        ),
        migrations.AlterField(
            model_name='jobmodel',
            name='priority',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
