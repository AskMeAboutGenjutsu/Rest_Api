# Generated by Django 4.0.6 on 2022-07-24 21:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Car', '0011_carsmodel_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCarRealation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like', models.BooleanField(default=False, verbose_name='Like')),
                ('rate', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Car.carsmodel', verbose_name='Объявление о машине')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]
