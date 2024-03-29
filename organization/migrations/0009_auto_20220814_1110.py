# Generated by Django 3.2.5 on 2022-08-14 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0008_auto_20220813_0557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='reg_id',
            field=models.IntegerField(blank=True, unique=True),
        ),
    ]
