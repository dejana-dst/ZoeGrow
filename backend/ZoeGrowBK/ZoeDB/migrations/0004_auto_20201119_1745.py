# Generated by Django 3.1.3 on 2020-11-19 16:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ZoeDB', '0003_auto_20201113_0412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendar',
            name='status',
            field=models.CharField(choices=[('NOT PLANTED', 'Not planted yet'), ('OUTSIDE', 'Planted outside'), ('INSIDE', 'Planted inside')], default='NOT PLANTED', max_length=30),
        ),
        migrations.AlterField(
            model_name='event',
            name='calendar',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='ZoeDB.calendar'),
        ),
        migrations.AlterField(
            model_name='plant',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/plants'),
        ),
    ]
