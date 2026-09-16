from django.urls import path

from main.views import (
    create_education,
    delete_education,
    get_education_json,
    show_education,
    show_experience,
    show_main,
)

app_name = "main"

urlpatterns = [
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