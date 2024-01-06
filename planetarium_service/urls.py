from django.urls import path, include
from rest_framework import routers

from planetarium_service.views import (AstronomyShowViewSet,
                                       ShowThemeViewSet,
                                       PlanetariumDomeViewSet,
                                       ShowSessionViewSet,
                                       ReservationViewSet)


router = routers.DefaultRouter()

router.register("astronomy_show", AstronomyShowViewSet)
router.register("show_theme", ShowThemeViewSet)
router.register("planetarium_dome", PlanetariumDomeViewSet)
router.register("show_session", ShowSessionViewSet)
router.register("reservation", ReservationViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "planetarium_service"
