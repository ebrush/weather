# Generated by Django 4.1.7 on 2023-03-09 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='weatherday',
            options={'ordering': ('station__code', 'date')},
        ),
        migrations.AlterModelOptions(
            name='weatherstats',
            options={'ordering': ('station__code', 'year')},
        ),
    ]