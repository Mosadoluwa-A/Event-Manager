# Generated by Django 3.2.5 on 2022-08-13 04:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0006_policies'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Policies',
            new_name='Policy',
        ),
        migrations.AlterModelOptions(
            name='policy',
            options={'verbose_name_plural': 'Policies'},
        ),
    ]