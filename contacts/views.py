from django.http import HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .models import Contact


def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, "contacts/index.html", {"contacts": contacts})


@require_http_methods(["POST"])
def contact_add(request):
    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip()
    if name and email:
        Contact.objects.create(name=name, email=email)
    contacts = Contact.objects.all()
    return render(request, "contacts/_contact_rows.html", {"contacts": contacts})


def contact_search(request):
    query = request.GET.get("q", "").strip()
    contacts = (
        Contact.objects.filter(name__icontains=query) if query else Contact.objects.all()
    )
    return render(request, "contacts/_contact_rows.html", {"contacts": contacts})


def contact_row(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, "contacts/_contact_row.html", {"contact": contact})


def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, "contacts/_contact_edit_row.html", {"contact": contact})


@require_http_methods(["PUT"])
def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    data = QueryDict(request.body)
    contact.name = data.get("name", contact.name)
    contact.email = data.get("email", contact.email)
    contact.save()
    return render(request, "contacts/_contact_row.html", {"contact": contact})


@require_http_methods(["DELETE"])
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    return HttpResponse("")
