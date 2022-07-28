from django.contrib.auth.models import User
from django.test import TestCase

from Car.logic import set_rating

from Car.models import LabelsModel, CarsModel, UserCarsRelation


class SetRatingTestCase(TestCase):
    def setUp(self):
        user_1 = User.objects.create(username='user_1', password=123, first_name='Альберт', last_name='Имаков')
        label_1 = LabelsModel.objects.create(name='Lada')
        self.car_1 = CarsModel.objects.create(
            label=label_1, model='Granta', year_of_release=2008, owner=user_1, price=250000,
            description='В хорошем состоянии', engine_type='d', transmission_type='a', drive_type='f', body_type='h',
            engine_capacity='1.6'
        )

        user_2 = User.objects.create(username='user_2', password=123, first_name='Марсель', last_name='Губайдуллин')
        user_3 = User.objects.create(username='user_3', first_name='Аркадий', last_name='Великородный')

        UserCarsRelation.objects.create(user=user_1, car=self.car_1, like=True, rate=2)
        UserCarsRelation.objects.create(user=user_2, car=self.car_1, like=True, rate=3)
        UserCarsRelation.objects.create(user=user_3, car=self.car_1, like=True, rate=5)

    def test_ok(self):
        set_rating(self.car_1)
        self.car_1.refresh_from_db()
        self.assertEqual('3.33', str(self.car_1.rating))