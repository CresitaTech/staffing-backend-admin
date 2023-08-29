# Generated by Django 3.1.4 on 2021-01-13 10:44

import candidatesdocumentrepositery.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('candidates', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='candidatesRepositeryModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('repo_name', models.CharField(max_length=255, null=True)),
                ('resume', models.FileField(blank=True, null=True, upload_to=candidatesdocumentrepositery.models.content_resume)),
                ('driving_license', models.FileField(blank=True, null=True, upload_to=candidatesdocumentrepositery.models.content_driving_license)),
                ('offer_letter', models.FileField(blank=True, null=True, upload_to=candidatesdocumentrepositery.models.content_offer_letter)),
                ('passport', models.FileField(blank=True, null=True, upload_to=candidatesdocumentrepositery.models.content_passport)),
                ('rtr', models.FileField(blank=True, null=True, upload_to=candidatesdocumentrepositery.models.content_rtr)),
                ('salary_slip', models.FileField(blank=True, null=True, upload_to=candidatesdocumentrepositery.models.content_salary_slip)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('candidate_name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='candidates.candidates')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='candidatesrepositerymodel_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='candidatesrepositerymodel_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Candidate Repositery',
                'verbose_name_plural': 'Candidates Repositeries',
                'db_table': 'osms_candidates_repositery',
            },
        ),
    ]
