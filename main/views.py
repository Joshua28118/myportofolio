from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import EducationForm, ExperienceForm, ProjectForm
from main.models import Education, Experience, Project


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


def create_experience(request):
    return _experience_form(request)


def edit_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    return _experience_form(request, experience)


def _experience_form(request, experience=None):
    editing = experience is not None
    form = ExperienceForm(
        request.POST if request.method == 'POST' else None,
        instance=experience,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(
            request,
            'Experience berhasil diperbarui.' if editing else 'Experience berhasil ditambahkan.',
        )
        return redirect('main:show_experience')
    return render(request, 'portfolio_form.html', {
        'name': 'Joshua Imanuel Setiawan',
        'heading': 'Edit Experience' if editing else 'Tambah Experience',
        'form': form,
        'cancel_route': 'main:show_experience',
    })


@require_POST
def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    experience.delete()
    messages.success(request, 'Experience berhasil dihapus.')
    return redirect('main:show_experience')


def get_projects_json(request):
    title_query = request.GET.get('title', '').strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    return HttpResponse(
        serializers.serialize('json', projects, indent=2),
        content_type='application/json',
    )


def show_projects(request):
    json_response = get_projects_json(request)
    projects = [row.object for row in serializers.deserialize(
        'json', json_response.content.decode('utf-8')
    )]
    return render(request, 'projects.html', {
        'name': 'Joshua Imanuel Setiawan',
        'project_list': projects,
        'title_query': request.GET.get('title', '').strip(),
    })


def create_project(request):
    form = ProjectForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Proyek berhasil ditambahkan.')
        return redirect('main:show_projects')
    return render(request, 'portfolio_form.html', {
        'name': 'Joshua Imanuel Setiawan',
        'heading': 'Tambah Proyek',
        'form': form,
        'cancel_route': 'main:show_projects',
    })


@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, 'Proyek berhasil dihapus.')
    return redirect('main:show_projects')
