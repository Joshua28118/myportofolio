from django import forms

from main.models import Education, Experience, Project


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


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['title', 'description', 'category', 'thumbnail', 'ended_at']
        labels = {
            'title': 'Judul Experience',
            'description': 'Deskripsi',
            'category': 'Kategori',
            'thumbnail': 'URL Gambar (opsional)',
            'ended_at': 'Tanggal dan Waktu Selesai',
        }
        help_texts = {
            'ended_at': 'Kosongkan jika pengalaman masih berlangsung.',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'ended_at': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}
            ),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'tech_stack', 'project_url']
        labels = {
            'title': 'Nama Proyek',
            'description': 'Deskripsi',
            'tech_stack': 'Teknologi yang Digunakan',
            'project_url': 'URL Proyek (opsional)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Personal Portfolio'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'tech_stack': forms.TextInput(attrs={'placeholder': 'Django, Python, HTML, CSS'}),
            'project_url': forms.URLInput(attrs={'placeholder': 'https://github.com/...'}),
        }
