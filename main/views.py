import datetime
from django.contrib import messages
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from main.forms import EducationForm, ExperienceForm, ProjectForm
from main.models import Education, Experience, Project

def show_main(request):
    last_login = request.COOKIES.get(
        "last_login",
        "No active login session / Cookie not found")
    context = {
        "name": "Joshua Imanuel Setiawan",
        "npm": "2506656854",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "A Computer Science student at Universitas Indonesia "
            "interested in software development and technology."
        ),
        "last_login": last_login
    }
    return render(request, "index.html", context)


def get_experience_json(request):
    experiences = Experience.objects.all()

    experience_json = serializers.serialize(
        "json",
        experiences,
        indent=2,
    )

    return HttpResponse(
        experience_json,
        content_type="application/json",
    )


def show_experience(request):
    json_response = get_experience_json(request)

    experience_objects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )

    experiences = [
        experience.object
        for experience in experience_objects
    ]

    context = {
        "name": "Joshua Imanuel Setiawan",
        "experience_list": experiences,
    }

    return render(request, "experience.html", context)


def get_education_json(request):
    institution_query = request.GET.get(
        "institution",
        "",
    ).strip()

    educations = Education.objects.all()

    if institution_query:
        educations = educations.filter(
            institution__icontains=institution_query,
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
            "institution",
            "",
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
    experience = get_object_or_404(
        Experience,
        pk=experience_id,
    )

    return _experience_form(request, experience)


def _experience_form(request, experience=None):
    editing = experience is not None

    form = ExperienceForm(
        request.POST if request.method == "POST" else None,
        instance=experience,
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            (
                "Experience berhasil diperbarui."
                if editing
                else "Experience berhasil ditambahkan."
            ),
        )

        return redirect("main:show_experience")

    context = {
        "name": "Joshua Imanuel Setiawan",
        "heading": (
            "Edit Experience"
            if editing
            else "Tambah Experience"
        ),
        "form": form,
        "cancel_route": "main:show_experience",
    }

    return render(
        request,
        "portfolio_form.html",
        context,
    )


@require_POST
def delete_experience(request, experience_id):
    experience = get_object_or_404(
        Experience,
        pk=experience_id,
    )

    experience.delete()

    messages.success(
        request,
        "Experience berhasil dihapus.",
    )

    return redirect("main:show_experience")


def get_projects_json(request):
    title_query = request.GET.get(
        "title",
        "",
    ).strip()

    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(
            title__icontains=title_query,
        )

    return HttpResponse(
        serializers.serialize(
            "json",
            projects,
            indent=2,
            use_natural_foreign_keys=True,
        ),
        content_type="application/json",
    )


def show_projects(request):
    json_response = get_projects_json(request)

    project_objects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )

    projects = [
        project.object
        for project in project_objects
    ]

    context = {
        "name": "Joshua Imanuel Setiawan",
        "project_list": projects,
        "title_query": request.GET.get(
            "title",
            "",
        ).strip(),
    }

    return render(request, "projects.html", context)


@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ProjectForm(
        request.POST if request.method == "POST" else None,
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Proyek berhasil ditambahkan.",
        )

        return redirect("main:show_projects")

    context = {
        "name": "Joshua Imanuel Setiawan",
        "heading": "Tambah Proyek",
        "form": form,
        "cancel_route": "main:show_projects",
    }

    return render(
        request,
        "portfolio_form.html",
        context,
    )


@login_required(login_url="/login/")
@require_POST
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(
        Project,
        pk=project_id,
    )

    project.delete()

    messages.success(
        request,
        "Proyek berhasil dihapus.",
    )

    return redirect("main:show_projects")

@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        if project.starred_by.filter(pk=request.user.pk).exists():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)
    return redirect("main:show_projects")


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("main:login")

    context = {
        "name": "Joshua Imanuel Setiawan",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        response = redirect("main:show_main")
        response.set_cookie(
            "last_login",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        return response
    context = {
        "name": "Joshua Imanuel Setiawan",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response
