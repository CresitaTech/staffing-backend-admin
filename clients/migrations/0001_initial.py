# Generated by Django 3.1.4 on 2021-01-13 10:22

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='clientModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('first_name', models.CharField(max_length=255, null=True)),
                ('last_name', models.CharField(max_length=255, null=True)),
                ('primary_email', models.CharField(max_length=255, null=True)),
                ('secondary_email', models.CharField(blank=True, max_length=255, null=True)),
                ('primary_phone_number', models.CharField(max_length=255, null=True)),
                ('secondary_phone_number', models.CharField(blank=True, max_length=255, null=True)),
                ('skype_id', models.CharField(blank=True, max_length=255, null=True)),
                ('linkedin_id', models.CharField(blank=True, max_length=255, null=True)),
                ('primary_skills', models.CharField(blank=True, max_length=255, null=True)),
                ('secondary_skills', models.CharField(blank=True, max_length=255, null=True)),
                ('company_name', models.CharField(max_length=255, null=True)),
                ('company_tin_number', models.CharField(blank=True, max_length=255, null=True)),
                ('total_employee', models.DecimalField(decimal_places=2, max_digits=50, null=True)),
                ('company_address', models.CharField(blank=True, max_length=255, null=True)),
                ('about_company', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('rank', models.IntegerField(blank=True, default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clientmodel_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clientmodel_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients List',
                'db_table': 'osms_clients',
            },
        ),
    ]
