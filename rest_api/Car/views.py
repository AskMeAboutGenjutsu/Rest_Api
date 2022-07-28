from django.db.models import Count, Case, When, Avg
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import CarsModel, UserCarsRelation, LabelsModel
from .permissions import IsAuthenticatedOwnerOrReadOnly, IsAdminUserOrReadOnly
from .serializers import CarsSerializer, UserCarsRelationSerializer, LabelsSerializer


class CarsAPIViewSet(ModelViewSet):
    queryset = CarsModel.objects.annotate(
            likes_count=Count(Case(When(usercarsrelation__like=True, then=1))))\
            .select_related('owner', 'label')\
            .prefetch_related('customers').order_by('id')
            # rating=Avg('usercarsrelation__rate'))\

    serializer_class = CarsSerializer
    permission_classes = [IsAuthenticatedOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price']
    search_fields = ['model', 'description', 'label__name']
    ordering_fields = ['year_of_release', 'price', 'date']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserCarsRelationView(UpdateModelMixin, GenericViewSet):
    queryset = UserCarsRelation.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserCarsRelationSerializer
    lookup_field = 'car'

    def get_object(self):
        obj, created = UserCarsRelation.objects.get_or_create(user=self.request.user, car_id=self.kwargs['car'])
        return obj


class LabelsView(mixins.CreateModelMixin,mixins.RetrieveModelMixin,
                 mixins.DestroyModelMixin,mixins.ListModelMixin,GenericViewSet):
    queryset = LabelsModel.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]
    serializer_class = LabelsSerializer


def index(request):
    return render(request, template_name='Car/index.html')
