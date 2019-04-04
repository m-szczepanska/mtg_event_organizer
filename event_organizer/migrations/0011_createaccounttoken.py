# Generated by Django 2.1.3 on 2019-04-04 15:41

import datetime
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('event_organizer', '0010_auto_20190319_2129'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreateAccountToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=200)),
                ('created_at', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('was_used', models.BooleanField(default=False)),
            ],
        ),
    ]
