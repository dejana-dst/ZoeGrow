# Generated by Django 3.1.3 on 2020-11-13 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ZoeDB', '0002_auto_20201113_0019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plant',
            name='feed_every_X_months',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plant',
            name='harvest_every_X_days',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plant',
            name='harvest_in_X_days',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plant',
            name='repot_every_X_years',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
