from django.db.models import Avg

from .models import UserCarsRelation


def set_rating(car):
    rating = UserCarsRelation.objects.filter(car=car).aggregate(rating=Avg('rate'))['rating']
    car.rating = rating
    car.save()