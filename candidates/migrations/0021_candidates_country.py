# Generated by Django 3.1.4 on 2022-09-19 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0020_candidates_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidates',
            name='country',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
