# Generated by Django 3.2.5 on 2022-09-07 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0011_team_motto'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='organizations', to='organization.team'),
        ),
        migrations.AddField(
            model_name='participant',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='participants', to='organization.team'),
        ),
    ]