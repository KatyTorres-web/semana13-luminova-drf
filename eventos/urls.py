from django.urls import path

from . import views

app_name = "eventos"
urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("eventos/", views.catalogo, name="catalogo"),
    path("eventos/<slug:slug>/", views.detalle, name="detalle"),
    path("eventos/<slug:slug>/reservar/", views.reservar, name="reservar"),
    path("reserva/exitosa/", views.reserva_exitosa, name="reserva_exitosa"),
    path("nosotros/", views.nosotros, name="nosotros"),
]
