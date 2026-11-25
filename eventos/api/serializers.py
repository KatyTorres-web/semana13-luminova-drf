from django.utils import timezone
from rest_framework import serializers

from eventos.models import Categoria, Evento, Reserva


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "slug", "icono"]
        read_only_fields = ["id"]


class EventoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source="categoria.nombre")
    cupos_disponibles = serializers.ReadOnlyField()
    estado_evento = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = [
            "id",
            "categoria",
            "categoria_nombre",
            "titulo",
            "slug",
            "descripcion",
            "fecha",
            "lugar",
            "ciudad",
            "precio",
            "capacidad",
            "activo",
            "cupos_disponibles",
            "estado_evento",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["id", "creado_en", "actualizado_en"]

    def get_estado_evento(self, evento) -> str:
        if not evento.es_futuro:
            return "finalizado"
        if not evento.activo:
            return "inactivo"
        if evento.cupos_disponibles == 0:
            return "agotado"
        return "disponible"

    def validate(self, attrs):
        fecha = attrs.get("fecha", getattr(self.instance, "fecha", None))
        capacidad = attrs.get("capacidad", getattr(self.instance, "capacidad", None))
        errores = {}

        if fecha is not None and fecha <= timezone.now():
            errores["fecha"] = "La fecha del evento debe ser futura."
        if capacidad is not None and capacidad < 1:
            errores["capacidad"] = "La capacidad debe ser mayor que cero."
        if errores:
            raise serializers.ValidationError(errores)

        return attrs


class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = ["id", "evento", "nombre", "correo", "cantidad", "estado", "fecha_reserva"]
        read_only_fields = ["id", "estado", "fecha_reserva"]

    def validate(self, attrs):
        evento = attrs.get("evento", getattr(self.instance, "evento", None))
        cantidad = attrs.get("cantidad", getattr(self.instance, "cantidad", 1))

        if evento is None:
            return attrs
        if not evento.activo or evento.fecha <= timezone.now():
            raise serializers.ValidationError({
                "evento": "Solo se pueden reservar entradas para eventos activos y futuros.",
            })
        if cantidad > evento.cupos_disponibles:
            raise serializers.ValidationError({
                "cantidad": "La cantidad solicitada supera los cupos disponibles.",
            })

        return attrs


class EventoHyperlinkedSerializer(EventoSerializer, serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="evento-detail")
    categoria = serializers.HyperlinkedRelatedField(
        view_name="categoria-detail",
        queryset=Categoria.objects.all(),
    )

    class Meta(EventoSerializer.Meta):
        fields = ["url", *EventoSerializer.Meta.fields]
