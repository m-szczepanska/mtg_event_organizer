# Generated by Django 2.1.3 on 2018-12-10 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_organizer', '0004_tournament_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]