from django.contrib.auth.models import User
from rest_framework import serializers

from .models import CarsModel, UserCarsRelation, LabelsModel


class CarsCustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class CarsSerializer(serializers.ModelSerializer):
    # likes_count = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner_name = serializers.CharField(source='owner.username', default='', read_only=True)
    # label = serializers.CharField(source='label')
    customers = CarsCustomersSerializer(many=True, read_only=True)

    class Meta:
        model = CarsModel
        fields = ('id', 'label', 'model', 'year_of_release',
                  'date', 'description', 'price', 'engine_type',
                  'engine_capacity', 'transmission_type', 'drive_type',
                  'body_type', 'owner_name', 'likes_count', 'rating', 'customers')

    # def get_likes_count(self, instance):
    #     return UserCarsRelation.objects.filter(car=instance, like=True).count()


class UserCarsRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCarsRelation
        fields = ('car', 'like', 'rate')


class LabelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabelsModel
        fields = '__all__'
