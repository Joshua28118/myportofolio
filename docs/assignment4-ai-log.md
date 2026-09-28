# Riwayat bantuan AI — Assignment 4

Tanggal: 28 September 2026. Alat: ChatGPT/Codex.

Ini ringkasan prompt dan tindakan dari percakapan pengerjaan, bukan transkrip lengkap atau bukti pengumpulan di SCELE.

| Prompt pengguna | Bantuan yang diberikan |
|---|---|
| “ini tugas 4 berikan saya apa yg disuruh isi pdf” | Membaca tugas-4.pdf dan merangkum prasyarat, role, star, keamanan JSON, dokumentasi, dan pengumpulan. |
| “berikan step by step cara pengerjaannya dengan jelas jangan bertele tele” | Menyusun urutan perubahan model, migrasi, view, URL, template, pengujian, dan dokumentasi. |
| “apakah kamu bisa mengerjakan dari instuksi pdf?” | Memeriksa lokasi proyek dan menemukan implementasi Tutorial 04 serta bagian yang belum memenuhi Assignment 4. |
| “yaa benar” | Mengonfirmasi folder proyek yang diperiksa untuk melanjutkan implementasi. |

## Bagian yang dibantu

- Pembatasan akses server untuk pemilik, editor, dan user biasa.
- Relasi star Experience, migrasi, view POST, CSRF, serta status dan jumlah star.
- Halaman detail Experience dan tombol sesuai role.
- Izin edit Project dan Education; pembatasan tambah/hapus Education.
- Daftar field publik pada JSON agar relasi akun tidak ikut terkirim.
- Validasi tujuan kembali setelah login agar tidak mengarah ke situs luar.
- Pengujian otomatis dan dokumentasi setup serta grup Editor di Django Admin.

## Batasan dan pemeriksaan

Kode disiapkan pada salinan kerja dan diuji dengan Django dari environment proyek. Pengujian role memakai akun sementara. Akun asli tidak otomatis ditetapkan sebagai editor. Pemilik proyek perlu memilih akun editor lewat Django Admin serta memeriksa status prasyarat Tutorial 04 dan pengumpulan di SCELE.

Bantuan AI tidak menjadi bukti mahasiswa sudah memahami setiap baris kode. Perbaikan selama sesi dilakukan oleh Codex; tidak dicatat sebagai pekerjaan manual mahasiswa. Dokumen ini tidak mengklaim adanya commit, push, atau pengumpulan sebelum tindakan tersebut benar-benar dilakukan.
