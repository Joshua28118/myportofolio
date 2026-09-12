from django.shortcuts import render
from main.models import Experience

def show_main(request):
    context = {
        "name": "Joshua Imanuel Setiawan",
        "npm": "2506656854",
        "study_program": "S1 Ilmu Komputer",
        "bio": "A Computer Science student at Universitas Indonesia interested in software development and technology.",
    }
    return render(request, "index.html", context)

def show_experience(request):
    context = {
        "name": "Joshua Imanuel Setiawan",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)