# Generated by Django 2.1.3 on 2018-12-30 20:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event_organizer', '0007_match_round'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='match',
            options={'ordering': ('round',)},
        ),
        migrations.AddField(
            model_name='tournament',
            name='rounds_number',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='match',
            name='player_2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player_2', to='event_organizer.Player'),
        ),
    ]