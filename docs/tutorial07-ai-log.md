# Riwayat bantuan AI - Tutorial 07

Tanggal: 9-10 November 2026. Alat: Claude.

Dokumen ini merangkum prompt dan bantuan dalam sesi pengerjaan. Ini bukan transkrip lengkap atau bukti pengumpulan di SCELE.

## Konteks dan prompt

| Prompt pengguna | Tindakan |
|---|---|
| "lihat di folder saya myportofolio ... beritahu saya myportofolio saya sudah sampai mana. baca dulu tutorial 0 sampai pdf akhir" | Membaca 18 PDF dan memeriksa isi repositori, lalu melaporkan posisi pengerjaan berhenti di Tutorial 05. |
| "lanjut ke tutorial 6 dulu kerjakan dengan bahasa yg standar programming, rapi dan sesuai dengan petunjuk pdf" | Membuat app `contacts` untuk Tutorial 06 dengan namespace terpisah agar tidak bentrok dengan app `main`. |
| "jangan kasih koment koment. pure kode aja" | Menghapus komentar pada kode yang ditulis AI dan menerapkannya untuk seterusnya. |
| "saya mau mengerjakan tugas 6 dulu, kerjakan sesuai isi pdf jangan menambahkan hal yg tidak di suruh. tanyakan saya dulu" | Menanyakan cakupan lebih dulu. Pengguna memilih mengerjakan Tutorial 07 terlebih dahulu karena Tugas 6 berpijak pada hasilnya. |

Strategi pengerjaan memakai PDF sebagai spesifikasi, lalu mencocokkannya dengan model, template, dan tes yang sudah ada di proyek.

## Bagian yang dibantu AI

- `main/serializers.py` berisi `ProjectSerializer` dengan daftar field eksplisit, `validate_title` yang menolak judul kosong setelah `strip_tags`, serta `star_count`, `is_starred`, dan `starred_by_names` sebagai `SerializerMethodField`.
- `main/api_views.py` berisi `project_list`, `project_detail`, dan `project_star` memakai `@api_view`, `SessionAuthentication`, dan pencarian `title__icontains`.
- `main/permissions.py` ditambah `IsPortfolioOwnerOrReadOnly` dan `IsPortfolioOwnerOrEditorOrReadOnly`. Decorator Assignment 4 di file yang sama tidak diubah.
- `main/api_urls.py` mendaftarkan tiga endpoint di bawah prefix `/api/v1/` dengan converter `<uuid:project_id>`.
- `templates/projects.html` memuat script inline yang mengambil data lewat `fetch`, dengan debounce 300 ms, `AbortController`, state loading/error/empty, modal, toast, dan `X-CSRFToken` pada operasi tulis.
- `main/tests_api.py` berisi 13 tes `APITestCase` sesuai PDF, termasuk dua tes CSRF.
- Catatan ini juga dibantu AI.

## Penyesuaian terhadap contoh PDF

- Field `project_image_url` pada contoh PDF dihapus dari serializer, payload tes, dan kartu karena model `Project` di proyek ini tidak memilikinya.
- ID input pencarian memakai `project-search` sesuai template yang sudah ada, bukan `search-input` seperti contoh.
- Kelas CSS kartu memakai kelas yang sudah dipakai proyek agar stylesheet lama tetap berlaku.
- Markup tombol Edit dan Hapus dibungkus `{% if %}` di template, bukan hanya dicek lewat konstanta JavaScript, sehingga HTML untuk peran yang tidak berwenang tidak memuat kontrol tersebut.
- Tombol Edit menuju halaman edit Assignment 3 dipertahankan atas permintaan pengguna, meskipun contoh PDF tidak memuatnya.

## Tes lama yang diubah

Empat assertion diubah karena kontraknya memang berganti. Tidak ada tes yang dihapus.

| File | Sebelum | Sesudah |
|---|---|---|
| `test_tutorial5.py` | `"js/projects.js"` | `reverse("api:project-list")` |
| `test_tutorial5.py` | `'class="project-delete"'` | `'project-delete'` |
| `test_portfolio_features.py` | `'id="project-card-template"'` | `reverse("api:project-list")` |
| `test_portfolio_features.py` | `assertNotContains('<script>')` | `assertNotContains('alert(1)')` |
| `test_assignment4.py` | URL `/projects/<id>/delete/` | penanda `data-action="delete"` |

## Hasil pemeriksaan

- 84 tes Django lulus pada mesin lokal, terdiri dari 71 tes lama dan 13 tes API baru.
- Pemeriksaan melalui HTTP pada salinan proyek di lingkungan AI: daftar publik 200, Browsable API 200, POST tanpa login 403, star tanpa login 403, detail UUID tak dikenal 404, dan halaman anonim tidak memuat kontrol Edit maupun Hapus.

## Batasan dan evaluasi bantuan AI

Pengujian interaksi di browser belum dilakukan. Klik tambah, star, hapus, serta pengetikan pada kolom pencarian belum pernah dijalankan pada peramban, sehingga perilaku modal, toast, dan debounce belum terbukti secara langsung. Pemeriksaan yang ada bersifat HTTP dan unit test.

Deploy ke PWS belum dilakukan, sehingga butir checklist mengenai situs yang berjalan setelah reinstall dependency belum terpenuhi.

Tenggat Tutorial 07 adalah 4 November 2026 dan pengerjaan ini dilakukan setelahnya. Menurut PDF, commit yang di-push setelah tenggat tidak diterima. Status penilaian ditentukan asisten, bukan oleh hasil pengujian lokal.

Kode pada sesi ini ditulis oleh AI. Dokumen ini tidak mengklaim adanya penulisan manual oleh mahasiswa maupun bahwa mahasiswa telah memahami setiap baris kode. Commit, push, pengumpulan SCELE, dan pemenuhan tenggat adalah langkah terpisah; hasil pengujian lokal tidak membuktikan langkah tersebut sudah selesai.
