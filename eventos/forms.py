from django import forms
from django.utils import timezone

from .models import Reserva


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ["nombre", "correo", "cantidad"]
        labels = {
            "nombre": "Nombre completo",
            "correo": "Correo electrónico",
            "cantidad": "Cantidad de entradas",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Tu nombre completo"}),
            "correo": forms.EmailInput(attrs={"placeholder": "ejemplo@correo.com"}),
            "cantidad": forms.NumberInput(attrs={"min": 1, "max": 10}),
        }

    def __init__(self, *args, evento=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.evento = evento

    def clean_cantidad(self):
        cantidad = self.cleaned_data["cantidad"]
        if not 1 <= cantidad <= 10:
            raise forms.ValidationError("Puedes solicitar entre 1 y 10 entradas.")
        return cantidad

    def clean(self):
        datos = super().clean()
        if self.evento is None:
            return datos

        if not self.evento.activo:
            raise forms.ValidationError("Este evento no está disponible.")
        if self.evento.fecha <= timezone.now():
            raise forms.ValidationError("No se aceptan reservas de eventos pasados.")

        cupos = self.evento.cupos_disponibles
        if cupos == 0:
            raise forms.ValidationError("No quedan cupos disponibles.")

        cantidad = datos.get("cantidad")
        if cantidad and cantidad > cupos:
            self.add_error(
                "cantidad",
                "La cantidad solicitada supera los cupos disponibles.",
            )

        return datos
