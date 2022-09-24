# Generated by Django 3.2.5 on 2022-09-07 21:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0012_auto_20220907_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teams', to='organization.category'),
        ),
    ]
