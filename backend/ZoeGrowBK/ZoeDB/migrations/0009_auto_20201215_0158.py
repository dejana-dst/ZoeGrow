# Generated by Django 3.1.3 on 2020-12-15 00:58

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ZoeDB', '0008_auto_20201215_0154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]