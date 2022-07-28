from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from Car.serializers import CarsSerializer, UserCarsRelationSerializer, LabelsSerializer

from Car.models import LabelsModel, CarsModel, UserCarsRelation


class CarsSerializerTestCase(TestCase):
    def test_data(self):
        user_1 = User.objects.create(username='user_1', password=123, first_name='Альберт', last_name='Имаков')
        label_1 = LabelsModel.objects.create(name='Lada')
        car_1 = CarsModel.objects.create(
            label=label_1, model='Granta', year_of_release=2008, owner=user_1, price=250000,
            description='В хорошем состоянии', engine_type='d', transmission_type='a', drive_type='f', body_type='h',
            engine_capacity='1.6'
        )

        user_2 = User.objects.create(username='user_2', password=123, first_name='Марсель', last_name='Губайдуллин')
        label_2 = LabelsModel.objects.create(name='Toyota')
        car_2 = CarsModel.objects.create(
            label=label_2, model='Camry', year_of_release=2018, owner=user_2, price=1250000,
            description='В отличном состоянии', engine_type='p', transmission_type='r', drive_type='a', body_type='u',
            engine_capacity='3.5'
        )

        UserCarsRelation.objects.create(user=user_1, car=car_1, like=True, rate=4)
        UserCarsRelation.objects.create(user=user_2, car=car_1, like=True, rate=3)
        UserCarsRelation.objects.create(user=user_1, car=car_2, like=True)
        UserCarsRelation.objects.create(user=user_2, car=car_2, like=False, rate=2)

        queryset = CarsModel.objects.annotate(
            likes_count=Count(Case(When(usercarsrelation__like=True, then=1)))).select_related('owner', 'label')\
            .prefetch_related('customers').order_by('id')

        data = CarsSerializer(queryset, many=True).data


        expected_data = [
            {
                'id': car_1.id,
                'model': 'Granta',
                'year_of_release': 2008,
                'date': car_1.date.isoformat(),
                'description': 'В хорошем состоянии',
                'engine_type': 'd',
                'engine_capacity': '1.6',
                'transmission_type': 'a',
                'drive_type': 'f',
                'body_type': 'h',
                'label': label_1.pk,
                'owner_name': user_1.username,
                'price': 250000,
                'likes_count': 2,
                'rating': '3.50',
                'customers': [
                    {
                        'first_name': user_1.first_name,
                        'last_name': user_1.last_name
                    },
                    {
                        'first_name': user_2.first_name,
                        'last_name': user_2.last_name
                    }
                ]
            },
            {
                'id': car_2.id,
                'model': 'Camry',
                'year_of_release': 2018,
                'date': car_2.date.isoformat(),
                'description': 'В отличном состоянии',
                'engine_type': 'p',
                'engine_capacity': '3.5',
                'transmission_type': 'r',
                'drive_type': 'a',
                'body_type': 'u',
                'label': label_2.pk,
                'owner_name': user_2.username,
                'price': 1250000,
                'likes_count': 1,
                'rating': '2.00',
                'customers': [
                    {
                        'first_name': user_1.first_name,
                        'last_name': user_1.last_name
                    },
                    {
                        'first_name': user_2.first_name,
                        'last_name': user_2.last_name
                    }
                ]
            }
        ]
        self.assertEqual(expected_data, data)


class UserCarsRelationTestCase(TestCase):
    def test_data(self):
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')

        label1 = LabelsModel.objects.create(name='Lada')

        car_1 = CarsModel.objects.create(
            label=label1, model='Granta', year_of_release=2008, owner=user1, price=250000,
            description='В хорошем состоянии', engine_type='d', transmission_type='a', drive_type='f', body_type='h',
            engine_capacity='1.6'
        )
        car_2 = CarsModel.objects.create(
            label=label1, model='Camry', year_of_release=2018, owner=user2, price=1250000,
            description='В отличном состоянии', engine_type='p', transmission_type='r', drive_type='a', body_type='u',
            engine_capacity='3.5'
        )
        rel1 = UserCarsRelation.objects.create(car=car_1, user=user1, like=True, rate=4)
        rel2 = UserCarsRelation.objects.create(car=car_2, user=user2, rate=5)

        data = UserCarsRelationSerializer([rel1, rel2], many=True).data

        expected_data = [
            {
                'car': car_1.id,
                'like': True,
                'rate': 4
            },
            {
                'car': car_2.id,
                'like': False,
                'rate': 5
            }
        ]

        self.assertEqual(expected_data, data)


class LabelsTestCase(TestCase):
    def test_data(self):
        label1 = LabelsModel.objects.create(name='Zaz')
        label2 = LabelsModel.objects.create(name='Uaz')
        data = LabelsSerializer([label1, label2], many=True).data

        expected_data = [
            {
                'name': 'Zaz',
            },
            {
                'name': 'Uaz',
            }
        ]

        self.assertEqual(expected_data, data)