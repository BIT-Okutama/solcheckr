# Generated by Django 2.1.3 on 2018-11-24 09:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkr', '0002_auto_20181115_0755'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='audit',
            name='github_repo',
        ),
        migrations.RemoveField(
            model_name='audit',
            name='github_user',
        ),
    ]
