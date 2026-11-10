import datetime
from django.contrib import messages
from django.core import serializers
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.http import url_has_allowed_host_and_scheme
from main.forms import EducationForm, ExperienceForm, ProjectForm
from main.models import Education, Experience, Project
from main.permissions import can_edit_portfolio, editor_required, owner_required


def _add_star_status(items, model, user):
    """Attach public counts and the current user's state after deserialization."""
    ids = [item.pk for item in items]
    counts = dict(
        model.objects.filter(pk__in=ids).annotate(total=Count("starred_by"))
        .values_list("pk", "total")
    )
    starred_ids = set()
    if user.is_authenticated:
        starred_ids = set(
            model.objects.filter(pk__in=ids, starred_by=user)
            .values_list("pk", flat=True)
        )
    for item in items:
        item.star_count = counts.get(item.pk, 0)
        item.is_starred = item.pk in starred_ids
    return items

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
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.order_by("-started_at", "pk")
    if title_query:
        experiences = experiences.filter(title__icontains=title_query)
    experiences = _add_star_status(list(experiences), Experience, request.user)
    data = [
        {
            "pk": str(experience.pk),
            "fields": {
                "title": experience.title,
                "description": experience.description,
                "category": experience.category,
                "category_display": experience.get_category_display(),
                "thumbnail": experience.thumbnail,
                "started_at": experience.started_at,
                "ended_at": experience.ended_at,
                "is_ongoing": experience.is_ongoing,
                "star_count": experience.star_count,
                "is_starred": experience.is_starred,
            },
        }
        for experience in experiences
    ]
    return JsonResponse(data, safe=False)


def show_experience(request):
    context = {
        "name": "Joshua Imanuel Setiawan",
        "form": ExperienceForm(),
        "edit_form": ExperienceForm(auto_id="id_edit_%s"),
        "title_query": request.GET.get("title", "").strip(),
        "can_edit": can_edit_portfolio(request.user),
    }
    return render(request, "experience.html", context)


@require_POST
def create_experience_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan Experience."},
            status=403,
        )
    form = ExperienceForm(request.POST)
    if form.is_valid():
        experience = form.save()
        return JsonResponse(
            {"message": "Experience berhasil ditambahkan.", "pk": str(experience.pk)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


def experience_detail(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    _add_star_status([experience], Experience, request.user)
    return render(request, "experience_detail.html", {
        "name": "Joshua Imanuel Setiawan",
        "experience": experience,
        "can_edit": can_edit_portfolio(request.user),
    })


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
        "can_edit": can_edit_portfolio(request.user),
        "institution_query": request.GET.get(
            "institution",
            "",
        ).strip(),
    }

    return render(request, "education.html", context)


@owner_required
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


@owner_required
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


@editor_required
def edit_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    form = EducationForm(
        request.POST if request.method == "POST" else None,
        instance=education,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Data pendidikan berhasil diperbarui.")
        return redirect("main:show_education")
    return render(request, "portfolio_form.html", {
        "name": "Joshua Imanuel Setiawan",
        "heading": "Edit Pendidikan",
        "form": form,
        "cancel_route": "main:show_education",
    })


@owner_required
def create_experience(request):
    return _experience_form(request)


@editor_required
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


@owner_required
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
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    projects = _add_star_status(list(projects), Project, request.user)
    data = [
        {
            "pk": str(project.pk),
            "fields": {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "project_url": project.project_url,
                "star_count": project.star_count,
                "is_starred": project.is_starred,
            },
        }
        for project in projects
    ]
    return JsonResponse(data, safe=False)


def show_projects(request):
    context = {
        "name": "Joshua Imanuel Setiawan",
        "form": ProjectForm(),
        "can_edit": can_edit_portfolio(request.user),
        "title_query": request.GET.get("title", "").strip(),
    }
    return render(request, "projects.html", context)


@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )
    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.pk)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@owner_required
def create_project(request):

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


@editor_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(
        request.POST if request.method == "POST" else None,
        instance=project,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui.")
        return redirect("main:show_projects")
    return render(request, "portfolio_form.html", {
        "name": "Joshua Imanuel Setiawan",
        "heading": "Edit Proyek",
        "form": form,
        "cancel_route": "main:show_projects",
    })


@owner_required
@require_POST
def delete_project(request, project_id):

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
@require_POST
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    return redirect("main:show_projects")


@login_required(login_url="main:login")
@require_POST
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
    else:
        experience.starred_by.add(request.user)
    if request.POST.get("return_to") == "detail":
        return redirect("main:experience_detail", experience_id=experience.pk)
    return redirect("main:show_experience")


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
    next_url = request.POST.get("next", request.GET.get("next", ""))
    if not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = ""
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        response = redirect(next_url or "main:show_main")
        response.set_cookie(
            "last_login",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        return response
    context = {
        "name": "Joshua Imanuel Setiawan",
        "form": form,
        "next": next_url,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response
