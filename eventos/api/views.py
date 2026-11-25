from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from eventos.models import Categoria, Evento, Reserva

from .permissions import LecturaPublicaEscrituraStaff
from .serializers import (
    CategoriaSerializer,
    EventoHyperlinkedSerializer,
    EventoSerializer,
    ReservaSerializer,
)


class PaginacionLuminova(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 20


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [LecturaPublicaEscrituraStaff]
    pagination_class = PaginacionLuminova
    filterset_fields = ["slug"]
    search_fields = ["nombre"]
    ordering_fields = ["nombre"]


class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.select_related("categoria").all()
    serializer_class = EventoSerializer
    permission_classes = [LecturaPublicaEscrituraStaff]
    pagination_class = PaginacionLuminova
    filterset_fields = ["activo", "ciudad", "categoria"]
    search_fields = ["titulo", "descripcion", "lugar", "ciudad"]
    ordering_fields = ["fecha", "precio", "titulo"]

    @action(detail=False, methods=["get"])
    def proximos(self, request):
        return self.list(request)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "proximos":
            queryset = queryset.filter(activo=True, fecha__gt=timezone.now())
        return queryset

    @action(detail=True, methods=["get"], serializer_class=EventoHyperlinkedSerializer)
    def enlaces(self, request, pk=None):
        return Response(self.get_serializer(self.get_object()).data)


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.select_related("evento").all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAdminUser]
    pagination_class = PaginacionLuminova
    filterset_fields = ["evento", "estado"]
    ordering_fields = ["fecha_reserva", "cantidad"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def pendientes(self, request):
        return self.list(request)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "pendientes":
            queryset = queryset.filter(estado="pendiente")
        return queryset
