# Generated by Django 4.0.6 on 2022-07-27 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Car', '0019_carsmodel_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carsmodel',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=3, null=True),
        ),
    ]
