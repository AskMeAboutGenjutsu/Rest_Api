import datetime

from django.contrib.auth.models import User
from django.db import models


def year_choices():
    return [(y, y) for y in range(1950, datetime.datetime.today().year)]


def engine_capacity_choices():
    return [(str(v/10), str(v/10)) for v in range(5, 61)]


class CarsModel(models.Model):
    label = models.ForeignKey('LabelsModel', on_delete=models.PROTECT, verbose_name='Марка авто')
    model = models.CharField(max_length=15, verbose_name='Модель авто')
    year_of_release = models.IntegerField(
        choices=year_choices(), default=datetime.datetime.today().year, verbose_name='Год выпуска')
    date = models.DateTimeField(verbose_name='Дата создания объявления', auto_now_add=True)
    description = models.TextField(verbose_name='Описание авто', null=True)
    price = models.IntegerField(verbose_name='Цена авто', null=True)

    engine_types = (
        ('p', 'Бензиновый'),
        ('d', 'Дизельный'),
    )
    engine_type = models.CharField(max_length=1, choices=engine_types, default='p', verbose_name='Тип двигателя')
    engine_capacity = models.CharField(
        max_length=3, choices=engine_capacity_choices(), default='1.5', verbose_name='Объем двигателя')

    transmission_types = (
        ('m', 'Механическая'),
        ('a', 'Автоматическая'),
        ('r', 'Роботизированная'),
    )
    transmission_type = models.CharField(
        max_length=1, choices=transmission_types, default='m', verbose_name='Тип КПП')

    drive_types = (
        ('f', 'Передний'),
        ('r', 'Задний'),
        ('a', 'Полный'),
    )
    drive_type = models.CharField(max_length=1, choices=drive_types, default='f', verbose_name='Привод')

    body_types = (
        ('h', 'Хэтбек'),
        ('s', 'Седан'),
        ('u', 'Универсал'),
        ('k', 'Кабриолет'),
    )
    body_type = models.CharField(max_length=1, choices=body_types, default='s', verbose_name='Кузов')

    owner = models.ForeignKey(User, verbose_name='Создатель объявления',
                              on_delete=models.CASCADE, null=True, related_name='my_book')

    customers = models.ManyToManyField(User, through='UserCarsRelation',
                                       related_name='rate_books', verbose_name='Оценка пользователей')

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

    def __str__(self):
        return f'{self.id}: {self.label} {self.model}: {self.year_of_release}'

    class Meta:
        verbose_name = 'Объявление о продаже авто'
        verbose_name_plural = 'Объявления о продаже авто'
        ordering = ['-date']


class LabelsModel(models.Model):
    name = models.CharField(max_length=20, verbose_name='Наименование марки авто', primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Марку автомобиля'
        verbose_name_plural = 'Марки автомобилей'
        ordering = ['name']


def rate_choices():
    return [(r, r) for r in range(1,6)]


class UserCarsRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    car = models.ForeignKey(CarsModel, on_delete=models.CASCADE, verbose_name='Объявление о машине')
    like = models.BooleanField(default=False, verbose_name='Like')
    rate = models.PositiveSmallIntegerField(choices=rate_choices(), verbose_name='Рейтинг', null=True)

    def __str__(self):
        return f'Отношение пользователя {self.user.username} к объявлению {self.car}'

    def save(self, *args, **kwargs):
        from .logic import set_rating

        creating = not self.pk

        old_rating = self.rate
        super().save(*args, **kwargs)
        new_rating = self.rate

        if old_rating != new_rating or creating:
            set_rating(self.car)

    class Meta:
        verbose_name = 'Отношение пользователя к объявлению'
        verbose_name_plural = 'Отношения пользователей к объявлениям'