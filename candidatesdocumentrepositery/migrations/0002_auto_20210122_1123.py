# Generated by Django 3.1.4 on 2021-01-22 11:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0007_auto_20210122_1123'),
        ('candidatesdocumentrepositery', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidatesrepositerymodel',
            name='candidate_name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='candidates.candidates'),
        ),
    ]
