from django.urls import path

from main.views import (
    create_experience,
    edit_experience,
    delete_experience,
    show_projects,
    create_project,
    delete_project,
    get_projects_json,
    create_education,
    delete_education,
    get_education_json,
    show_education,
    show_experience,
    show_main,
)

app_name = "main"

urlpatterns = [
    path('experience/add/', create_experience, name='create_experience'),
    path('experience/<uuid:experience_id>/edit/', edit_experience, name='edit_experience'),
    path('experience/<uuid:experience_id>/delete/', delete_experience, name='delete_experience'),
    path('projects/', show_projects, name='show_projects'),
    path('projects/add/', create_project, name='create_project'),
    path('projects/<uuid:project_id>/delete/', delete_project, name='delete_project'),
    path('api/projects/', get_projects_json, name='get_projects_json'),
    path("", show_main, name="show_main"),
    path(
        "experience/",
        show_experience,
        name="show_experience",
    ),
    path(
        "education/",
        show_education,
        name="show_education",
    ),
    path(
        "education/add/",
        create_education,
        name="create_education",
    ),
    path(
        "education/<uuid:education_id>/delete/",
        delete_education,
        name="delete_education",
    ),
    path(
        "api/education/",
        get_education_json,
        name="get_education_json",
    ),
]
