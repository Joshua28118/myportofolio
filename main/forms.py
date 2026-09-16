from django import forms

from main.models import Education


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education

        fields = [
            "institution",
            "program",
            "description",
            "started_at",
            "ended_at",
        ]

        labels = {
            "institution": "Nama Institusi",
            "program": "Program Pendidikan",
            "description": "Deskripsi",
            "started_at": "Tanggal Mulai",
            "ended_at": "Tanggal Selesai",
        }

        help_texts = {
            "ended_at": "Kosongkan jika pendidikan masih berlangsung.",
        }

        widgets = {
            "institution": forms.TextInput(
                attrs={
                    "placeholder": "Universitas Indonesia",
                }
            ),
            "program": forms.TextInput(
                attrs={
                    "placeholder": "S1 Ilmu Komputer",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Ceritakan pendidikan kamu.",
                    "rows": 4,
                }
            ),
            "started_at": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
            "ended_at": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
        }