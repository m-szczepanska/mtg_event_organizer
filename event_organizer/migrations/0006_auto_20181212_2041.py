# Generated by Django 2.1.3 on 2018-12-12 20:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event_organizer', '0005_auto_20181210_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='player_1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_1', to='event_organizer.Player'),
        ),
        migrations.AlterField(
            model_name='match',
            name='player_2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_2', to='event_organizer.Player'),
        ),
        migrations.AlterField(
            model_name='match',
            name='tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='event_organizer.Tournament'),
        ),
    ]
