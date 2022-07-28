from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from Car.views import CarsAPIViewSet, UserCarsRelationView, LabelsView


router = SimpleRouter()
router.register('cars', CarsAPIViewSet)
router.register('cars_relation', UserCarsRelationView)
router.register('labels', LabelsView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),

]

urlpatterns += router.urls


if settings.DEBUG:
    import debug_toolbar

    import mimetypes

    mimetypes.add_type("application/javascript", ".js", True)

    urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
