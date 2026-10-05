# Riwayat bantuan AI - Assignment 5

Tanggal: 5 Oktober 2026. Alat: ChatGPT/Codex.

Dokumen ini merangkum prompt dan bantuan dalam sesi pengerjaan. Ini bukan transkrip lengkap atau bukti pengumpulan di SCELE.

## Konteks dan prompt

| Prompt pengguna | Tindakan |
|---|---|
| "kamu ingat tutorial dan tugas pbp yg pernah saya kasih sebelumnya, sekarang ada tutorial 5 kerjakan sesuai instruksi pdf dan tutorial serta tugas sebelumnya secara otomatis, jgn berikan comment baru hanya kode yg rapi saja" | Menyiapkan fondasi Tutorial 5 pada Projects, menguji fitur, dan mempertahankan aturan akses tugas sebelumnya. |
| "sekarang tugas 5", dengan tugas-5.pdf | Membaca seluruh empat halaman PDF, memeriksa commit Tutorial 5 dan proyek aktif, lalu menerapkan pola AJAX ke Experience dari Assignment 3 dan 4. |

Strategi pengerjaan menggunakan PDF sebagai spesifikasi, lalu mencocokkannya dengan model, form, template, serta tes yang sudah ada. Permintaan tanpa komentar kode baru tetap diterapkan walaupun rubrik memberi contoh komentar/docstring sebagai salah satu opsi peningkatan kualitas.

## Bagian yang dibantu AI

- JSON Experience dibuat dengan JsonResponse dan hanya berisi data publik, jumlah star, serta status star pengguna aktif.
- Daftar Experience memuat kerangka halaman sebelum mengambil data melalui fetch.
- Pencarian judul menggunakan debounce 300 ms, pembatalan request lama, Reset, serta pemulihan melalui Coba lagi.
- Modal tambah Experience memakai ModelForm, POST, CSRF, dan respons JSON 201/400/403.
- Toast dipakai untuk hasil sukses, kesalahan validasi, kegagalan jaringan, dan kegagalan memuat daftar.
- Teks ditampilkan dengan textContent. Judul dan deskripsi dibersihkan melalui strip_tags, dan hasil kosong ditolak. URL gambar divalidasi di server dan diperiksa protokolnya saat dirender.
- Hak akses pengunjung, pengguna biasa, staff, Editor, dan superuser diperiksa di server. Halaman detail, edit, star/unstar, dan konfirmasi hapus tetap tersedia.
- Tes lama disesuaikan karena daftar kini dirender di browser. Tes Assignment 5, jawaban refleksi README, dan catatan ini juga dibantu AI.

## Hasil pemeriksaan

- 71 tes Django lulus, termasuk 13 tes Assignment 5 dengan beberapa kasus input dan peran pada setiap tes.
- Pemeriksaan konfigurasi Django tidak menemukan masalah dan pemeriksaan migrasi tidak mendeteksi perubahan model.
- 45 pemeriksaan browser otomatis lulus menggunakan Microsoft Edge pada server lokal dan salinan database. Cakupannya termasuk seluruh peran, debounce, tanpa reload, empty/error state, retry, modal, toast, XSS, CSRF, star/unstar, konfirmasi hapus, sesi login berakhir, serta kegagalan jaringan dan respons non-JSON.
- Tampilan desktop dan modal pada viewport ponsel diperiksa dari tangkapan layar browser. Tidak ditemukan error JavaScript selama pengujian.
- Pengujian browser menggunakan akun dan data sementara pada salinan kerja. Database asli tidak dipakai untuk membuat data uji.

## Batasan dan evaluasi bantuan AI

AI tidak otomatis mengetahui struktur proyek. Contoh Projects pada Tutorial 5 harus disesuaikan dengan kategori, thumbnail, tanggal, detail, dan aturan akses Experience. Respons sukses, lokasi endpoint, dan label diperiksa agar tidak tertinggal sebagai nama Projects. Assertion tes lama yang mencari kartu dalam HTML awal juga diubah untuk memeriksa JSON, sementara hasil render diuji melalui browser.

strip_tags dapat menghilangkan teks yang menyerupai tag HTML dan tidak menjamin hasilnya aman sebagai HTML. Karena itu, perlindungan utama tetap textContent saat menampilkan data. Pengujian yang lulus mencakup skenario yang dijalankan, bukan jaminan bebas bug pada semua kondisi atau semua browser.

Perbaikan dan pengujian pada sesi ini dilakukan oleh Codex. Dokumen ini tidak mengklaim adanya perbaikan manual oleh mahasiswa maupun bahwa mahasiswa telah memahami setiap baris kode. Commit, push, pengumpulan SCELE, dan pemenuhan tenggat adalah langkah terpisah; hasil pengujian lokal tidak membuktikan langkah tersebut sudah selesai.
