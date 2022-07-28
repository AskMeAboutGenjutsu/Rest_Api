import json

from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Case, When, Avg
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from Car.models import CarsModel, LabelsModel, UserCarsRelation

from Car.serializers import CarsSerializer


class CarAPITestCase(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='user_1', password=123)
        self.label_1 = LabelsModel.objects.create(name='Lada')
        self.car_1 = CarsModel.objects.create(label=self.label_1, model='Granta', year_of_release=2008,
                                              owner=self.user_1, price=100000)

        self.user_2 = User.objects.create(username='user_2', password=123)
        self.label_2 = LabelsModel.objects.create(name='Toyota')
        self.car_2 = CarsModel.objects.create(label=self.label_2, model='Camry', year_of_release=2020,
                                              owner=self.user_2, price=100000)

        self.user_3 = User.objects.create(username='user_3', password=123)
        self.label_3 = LabelsModel.objects.create(name='Subaru')
        self.car_3 = CarsModel.objects.create(label=self.label_3, model='impreza', year_of_release=2018,
                                              owner=self.user_3, description='Двигатель от toyota',
                                              price=250000)
        UserCarsRelation.objects.create(car=self.car_1, user=self.user_1, like=True, rate=5)

    def test_get(self):
        url = reverse('carsmodel-list')
        response = self.client.get(url)

        queryset = CarsModel.objects.annotate(
            likes_count=Count(Case(When(usercarsrelation__like=True, then=1)))).select_related('owner', 'label')\
            .prefetch_related('customers').order_by('id')
        serializer_data = CarsSerializer(queryset, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('carsmodel-list')
        response = self.client.get(url, data={'price': 100000})
        queryset = CarsModel.objects.filter(id__in=[self.car_1.id, self.car_2.id]).annotate(
            likes_count=Count(Case(When(usercarsrelation__like=True, then=1)))).select_related('owner', 'label')\
            .prefetch_related('customers').order_by('id')
        serializer_data = CarsSerializer(queryset, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('carsmodel-list')
        response = self.client.get(url, data={'search': 'Toyota'})
        queryset = CarsModel.objects.filter(id__in=[self.car_2.id, self.car_3.id]).annotate(
            likes_count=Count(Case(When(usercarsrelation__like=True, then=1)))).select_related('owner', 'label')\
            .prefetch_related('customers').order_by('id')
        serializer_data = CarsSerializer(queryset, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_order(self):
        url = reverse('carsmodel-list')
        response = self.client.get(url, data={'ordering': 'year_of_release'})
        queryset = CarsModel.objects.annotate(
            likes_count=Count(Case(When(usercarsrelation__like=True, then=1)))).select_related('owner', 'label')\
            .prefetch_related('customers').order_by('year_of_release')
        serializer_data = CarsSerializer(queryset, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_alone(self):
        url = reverse('carsmodel-detail', args=(self.car_1.id,))
        response = self.client.get(url)
        queryset = CarsModel.objects.filter(id=self.car_1.id).annotate(
            likes_count=Count(Case(When(usercarsrelation__like=True, then=1)))).select_related('owner', 'label')\
            .prefetch_related('customers')
        serializer_data = CarsSerializer(queryset[0]).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        url = reverse('carsmodel-list')
        self.client.force_login(self.user_1)
        data = {
                'model': 'Priora',
                'year_of_release': 2012,
                'description': 'В нормальном состоянии',
                'label': self.label_1.pk,
                'price': 250000
        }

        json_data = json.dumps(data)

        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, CarsModel.objects.all().count())

    def test_update(self):
        url = reverse('carsmodel-detail', args=(self.car_1.id,))
        self.client.force_login(self.user_1)
        data = {
                'label': self.label_2.pk,
                'model': 'Priora',
                'year_of_release': 2008,
                'price': 150000,
        }

        json_data = json.dumps(data)

        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = {'id': self.car_1.id,
                         'model': 'Priora',
                         'year_of_release': 2008,
                         'date': self.car_1.date.isoformat(),
                         'description': None,
                         'price': 150000,
                         'engine_type': 'p',
                         'engine_capacity': '1.5',
                         'transmission_type': 'm',
                         'drive_type': 'f',
                         'body_type': 's',
                         'label': 'Toyota',
                         'owner_name': self.user_1.username,
                         'likes_count': 1,
                         'rating': '5.00',
                         'customers': [
                             {
                                 'first_name': self.user_1.first_name,
                                 'last_name': self.user_1.last_name
                             }
                         ]
                         }

        self.assertEqual(expected_data, response.data)

    def test_delete(self):
        url = reverse('carsmodel-detail', args=(self.car_1.id,))
        self.client.force_login(self.user_1)

        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        self.assertEqual(2, CarsModel.objects.all().count())

    def test_update_not_owner(self):
        url = reverse('carsmodel-detail', args=(self.car_1.id,))
        self.client.force_login(self.user_2)
        data = {
            'label': 'Lada',
            'model': 'Priora',
            'year_of_release': 2008,
            'price': 150000,
        }

        json_data = json.dumps(data)

        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.client.logout()

    def test_update_not_auth(self):
        url = reverse('carsmodel-detail', args=(self.car_1.id,))
        data = {
            'label': 'Lada',
            'model': 'Priora',
            'year_of_release': 2008,
            'price': 150000,
        }

        json_data = json.dumps(data)

        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_update_is_staff(self):
        user_staff = User.objects.create(username='admin', is_staff=True)
        url = reverse('carsmodel-detail', args=(self.car_1.id,))
        self.client.force_login(user_staff)
        data = {
            'label': 'Lada',
            'model': 'Priora',
            'year_of_release': 2008,
            'price': 150000,
        }

        json_data = json.dumps(data)

        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = {'id': self.car_1.id,
                         'model': 'Priora',
                         'year_of_release': 2008,
                         'date': self.car_1.date.isoformat(),
                         'description': None,
                         'price': 150000,
                         'engine_type': 'p',
                         'engine_capacity': '1.5',
                         'transmission_type': 'm',
                         'drive_type': 'f',
                         'body_type': 's',
                         'label': 'Lada',
                         'owner_name': self.user_1.username,
                         'likes_count': 1,
                         'rating': '5.00',
                         'customers': [
                             {
                                 'first_name': self.user_1.first_name,
                                 'last_name': self.user_1.last_name
                             }
                         ]}

        self.assertEqual(expected_data, response.data)


class UserCarRelationAPITestCase(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='loh', password=123)
        self.label_1 = LabelsModel.objects.create(name='Lada')
        self.car_1 = CarsModel.objects.create(label=self.label_1, model='Granta', year_of_release=2008,
                                              owner=self.user_1, price=100000)

        self.user_2 = User.objects.create(username='loh2', password=123)
        self.label_2 = LabelsModel.objects.create(name='Toyota')
        self.car_2 = CarsModel.objects.create(label=self.label_2, model='Camry', year_of_release=2020,
                                              owner=self.user_2, price=100000)

    def test_like(self):
        url = reverse('usercarsrelation-detail', args=(self.car_1.id,))
        data = {
            'like': True,
        }
        json_data = json.dumps(data)

        self.client.force_login(self.user_2)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserCarsRelation.objects.get(car_id=self.car_1.id, user=self.user_2)
        # self.assertTrue(self.car_1.usercarsrelation_set.get(car_id=self.car_1.id, user=self.user_2).like)
        self.assertTrue(relation.like)

    def test_like_and_rate(self):
        url = reverse('usercarsrelation-detail', args=(self.car_2.id,))
        self.client.force_login(self.user_1)
        data = {
            'like': True,
            'rate': 5,
        }
        json_data = json.dumps(data)

        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserCarsRelation.objects.get(car_id=self.car_2.id, user=self.user_1)
        # self.assertTrue(self.car_1.usercarsrelation_set.get(car_id=self.car_1.id, user=self.user_2).like)
        self.assertTrue(relation.like)
        self.assertEqual(5, relation.rate)


class LabelsApiTestCase(APITestCase):
    def setUp(self):
        self.label1 = LabelsModel.objects.create(name='BMW')
        self.label2 = LabelsModel.objects.create(name='Audi')
        self.admin = User.objects.create(username='admin', is_staff=True)
        self.user = User.objects.create(username='user')

    def test_get(self):
        url = reverse('labelsmodel-list')
        response = self.client.get(url)

        data = [
            {
                'name': 'Audi'
            },
            {
                'name': 'BMW'
            }
        ]

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(data, response.data)

    def test_get_alone(self):
        url = reverse('labelsmodel-detail', args=(self.label1.pk,))
        response = self.client.get(url)

        data = {
                'name': 'BMW'
        }

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(data, response.data)

    def test_create_is_staff(self):
        self.client.force_login(self.admin)
        url = reverse('labelsmodel-list')
        data = {
            'name': 'Ford'
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, LabelsModel.objects.all().count())

    def test_create_wrong(self):
        self.client.force_login(self.user)
        url = reverse('labelsmodel-list')
        data = {
            'name': 'Kia'
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(2, LabelsModel.objects.all().count())

    def test_delete_is_staff(self):
        self.client.force_login(self.admin)
        url = reverse('labelsmodel-detail', args=(self.label2.pk,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(1, LabelsModel.objects.all().count())

    def test_delete_wrong(self):
        self.client.force_login(self.user)
        url = reverse('labelsmodel-detail', args=(self.label2.pk,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(2, LabelsModel.objects.all().count())