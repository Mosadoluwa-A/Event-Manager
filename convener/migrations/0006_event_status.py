# Generated by Django 3.2.5 on 2022-06-13 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('convener', '0005_convener_email_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='status',
            field=models.CharField(blank=True, choices=[('ongoing', 'Ongoing'), ('concluded', 'Concluded')], max_length=10),
        ),
    ]
