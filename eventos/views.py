from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ReservaForm
from .models import Categoria, Evento


def inicio(request):
    proximos = Evento.objects.filter(activo=True, fecha__gt=timezone.now())
    return render(request, "eventos/inicio.html", {
        "total_eventos": proximos.count(),
        "total_categorias": Categoria.objects.count(),
        "destacados": proximos.select_related("categoria")[:3],
    })


def catalogo(request):
    busqueda = request.GET.get("q", "").strip()
    categoria_actual = request.GET.get("categoria", "").strip()
    eventos = Evento.objects.filter(activo=True).select_related("categoria")

    if busqueda:
        eventos = eventos.filter(
            Q(titulo__icontains=busqueda) | Q(ciudad__icontains=busqueda)
        )
    if categoria_actual:
        eventos = eventos.filter(categoria__slug=categoria_actual)

    return render(request, "eventos/catalogo.html", {
        "eventos": eventos,
        "categorias": Categoria.objects.all(),
        "busqueda": busqueda,
        "categoria_actual": categoria_actual,
    })


def detalle(request, slug):
    evento = get_object_or_404(
        Evento.objects.select_related("categoria"), slug=slug, activo=True
    )
    return render(request, "eventos/detalle.html", {"evento": evento})


def reservar(request, slug):
    evento = get_object_or_404(Evento, slug=slug, activo=True)
    if request.method == "POST":
        form = ReservaForm(request.POST, evento=evento)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.evento = evento
            reserva.estado = "pendiente"
            reserva.save()
            messages.success(request, "Tu solicitud fue registrada correctamente.")
            return redirect("eventos:reserva_exitosa")
    else:
        form = ReservaForm(evento=evento)

    return render(request, "eventos/reservar.html", {"evento": evento, "form": form})


def reserva_exitosa(request):
    return render(request, "eventos/reserva_exitosa.html")


def nosotros(request):
    return render(request, "eventos/nosotros.html")
