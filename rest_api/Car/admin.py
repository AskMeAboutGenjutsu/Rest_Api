from django.contrib import admin

from .models import LabelsModel, CarsModel, UserCarsRelation

admin.site.register(LabelsModel)
admin.site.register(CarsModel)
admin.site.register(UserCarsRelation)