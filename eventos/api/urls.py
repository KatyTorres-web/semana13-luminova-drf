from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoriaViewSet, EventoViewSet, ReservaViewSet

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("eventos", EventoViewSet, basename="evento")
router.register("reservas", ReservaViewSet, basename="reserva")

urlpatterns = [
    path("", include(router.urls)),
]
