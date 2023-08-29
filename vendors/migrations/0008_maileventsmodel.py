# Generated by Django 3.1.4 on 2021-09-10 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0007_auto_20210910_0403'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailEventsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('maildata', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'mail_events',
            },
        ),
    ]
