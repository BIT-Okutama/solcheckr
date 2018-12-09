# Generated by Django 2.1.3 on 2018-12-09 05:48

import checkr.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkr', '0002_auto_20181204_0557'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZipAudit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report', models.TextField(blank=True, default='')),
                ('result', models.NullBooleanField()),
                ('submitted', models.DateTimeField(auto_now=True)),
                ('tracking', models.CharField(blank=True, max_length=100, null=True)),
                ('contracts', models.TextField(blank=True, default='')),
            ],
            options={
                'abstract': False,
            },
            bases=(checkr.models.TrackingMixin, models.Model),
        ),
    ]
