from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import EducationForm
from main.models import Education, Experience


def show_main(request):
    context = {
        "name": "Joshua Imanuel Setiawan",
        "npm": "2506656854",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "A Computer Science student at Universitas Indonesia "
            "interested in software development and technology."
        ),
    }

    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Joshua Imanuel Setiawan",
        "experience_list": Experience.objects.all(),
    }

    return render(request, "experience.html", context)


def get_education_json(request):
    institution_query = request.GET.get("institution", "").strip()

    educations = Education.objects.all()

    if institution_query:
        educations = educations.filter(
            institution__icontains=institution_query
        )

    education_json = serializers.serialize(
        "json",
        educations,
        indent=2,
    )

    return HttpResponse(
        education_json,
        content_type="application/json",
    )


def show_education(request):
    json_response = get_education_json(request)

    education_objects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )

    educations = [
        education.object
        for education in education_objects
    ]

    context = {
        "name": "Joshua Imanuel Setiawan",
        "educations": educations,
        "institution_query": request.GET.get(
            "institution", ""
        ).strip(),
    }

    return render(request, "education.html", context)


def create_education(request):
    if request.method == "POST":
        form = EducationForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Data pendidikan berhasil ditambahkan!",
            )

            return redirect("main:show_education")
    else:
        form = EducationForm()

    context = {
        "name": "Joshua Imanuel Setiawan",
        "form": form,
    }

    return render(request, "education_form.html", context)


@require_POST
def delete_education(request, education_id):
    education = get_object_or_404(
        Education,
        pk=education_id,
    )

    institution = education.institution
    education.delete()

    messages.success(
        request,
        f'Data pendidikan "{institution}" berhasil dihapus.',
    )

    return redirect("main:show_education")