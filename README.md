Name : Joshua Imanuel Setiawan
NPM : 2506656854
Class : PBP D

### Assignment 1
1. Semantic HTML5
Saya pakai elemen semantic HTML5 — <section>, <article>, <header>, <nav>, <main>, <footer> — untuk membangun halaman portofolio ini. <section> memisahkan bagian Profile dan Education, <article> membungkus tiap item pendidikan. Orang yang buka source code-nya langsung paham strukturnya tanpa perlu baca CSS dulu.

2. Tampilan responsif
Tantangan terbesarnya: menjaga layout tetap rapi di layar kecil. Desktop pakai grid beberapa kolom; media query mengubahnya jadi satu kolom di mobile. Profil, foto, dan riwayat pendidikan saya taruh di posisi yang mudah dilihat di kedua ukuran layar, jadi keterbacaan tidak hilang saat layar menyempit.

3. Rencana pengembangan
Website ini masih statis — belum terhubung database, jadi tiap update informasi berarti ubah kode langsung. Ke depannya saya mau tambahkan section project yang datanya diambil dari database, plus form kontak supaya pengunjung bisa kirim pesan langsung dari halaman.

### Assignment 2
1. Saat pengguna membuka halaman Education, request pertama masuk ke urls.py di level project. URL project meneruskan request itu ke konfigurasi URL aplikasi main. Di main/urls.py, path education/ terhubung ke view show_education. View show_education mengambil seluruh data Education dari database lewat Education.objects.all(), memasukkannya ke context, lalu mengirim context itu ke template education.html. Model Education menentukan struktur data pendidikan yang tersimpan di database: institution, program, description, started_at, dan ended_at. Template education.html menerima data dari view dan menampilkan tiap objek Education pakai Django Template Language. Browser menerima HTML hasil render itu. Alurnya:
Browser Request -> Project urls.py -> Application urls.py -> View -> Model -> Context -> Template -> Browser

2. Data Education masuk ke model, bukan ditulis langsung di template, karena itu memisahkan data dari tampilan. Kalau data ditulis langsung di HTML, tiap perubahan data berarti mengedit template secara manual, dan aplikasi makin sulit dirawat seiring bertambahnya data.Dengan model Education, saya mengelola data lewat database tanpa menyentuh struktur HTML. Template hanya menampilkan apa yang dikirim view. Saya bisa menambah, mengubah, atau menghapus data Education, dan memakai data yang sama di halaman atau fitur lain, tanpa mengubah template sama sekali.

3. makemigrations dan migrate menjalankan dua tahap berbeda dalam Django.python manage.py makemigrations mendeteksi perubahan pada model dan membuat file migration berisi instruksi perubahan struktur database. python manage.py migrate menerapkan file migration itu ke database sampai strukturnya sesuai dengan model. Pada Assignment 2, saya menambahkan model baru bernama Education dengan field institution, program, description, started_at, dan ended_at. Setelah membuat model itu, saya menjalankan python manage.py makemigrations, yang membuat file migration baru untuk model Education. Lalu saya menjalankan python manage.py migrate, yang menerapkan migration itu dan membuat tabel Education di database.

### Assignment 3
1. Django ModelForm mempercepat pembuatan form: field, validasi dasar, dan proses penyimpanan otomatis mengikuti struktur model, sehingga tidak perlu menulis HTML form dan logika validasi manual satu per satu. Ini memangkas pengulangan kode dan menjaga tipe data yang masuk tetap sesuai dengan field pada model. {% csrf_token %} melindungi form dari serangan Cross-Site Request Forgery. Token ini memastikan request POST benar-benar berasal dari halaman aplikasi Django yang sedang dipakai, bukan dari situs lain yang mengirim form diam-diam lewat sesi pengguna.

2. JSON lebih umum dipakai di pengembangan web modern karena formatnya ringan dan mudah dibaca, baik oleh manusia maupun JavaScript. JavaScript bisa langsung mengonversi JSON menjadi object, sehingga cocok untuk pertukaran data antara frontend dan backend. XML memakai tag pembuka dan penutup untuk tiap elemen, sehingga ukuran datanya lebih besar dan proses pembacaannya lebih lambat dibanding JSON.

3. Saat view mengembalikan data portfolio dalam JSON, view mengambil data dari database melalui model Django, misalnya Experience.objects.all(). Data tersebut diubah menjadi JSON dengan serializers.serialize(), lalu dikirim melalui HttpResponse dengan content_type="application/json". Serialisasi diperlukan karena objek model Django bukan data mentah yang bisa langsung dikirim lewat HTTP — objek ini membawa atribut, tipe data, dan relasi ke database. Serialisasi mengubah objek tersebut menjadi format JSON yang bisa dikirim, dibaca, dan dipakai halaman atau aplikasi lain. Pada halaman Experience, JSON ini dideserialisasi kembali sebelum ditampilkan di template.

### Assignment 4 
1. Pada Assignment 4, saya melanjutkan bagian Experience dengan menerapkan autentikasi dan pembatasan hak akses. Registrasi, login, dan logout memakai sistem autentikasi bawaan Django dari Tutorial 04. Session menyimpan status login pengguna, sedangkan cookie last_login menampilkan waktu login terakhir dan dihapus saat logout. Pengunjung bisa membaca daftar dan detail Experience tanpa login. User biasa bisa memberikan star, Editor bisa mengedit data, dan superuser sebagai pemilik portofolio bisa menambah, mengedit, serta menghapus data. Pemeriksaan izin dilakukan di view, sehingga membuka URL secara langsung tetap tidak bisa melewati pembatasan. Pengunjung yang belum login diarahkan ke halaman login, sedangkan pengguna yang tidak memiliki izin mendapat HTTP 403 Forbidden. Tombol pada halaman juga ditampilkan sesuai hak akses.

2. Role Editor menggunakan Django Group bernama Editor. Untuk menetapkannya, pemilik login ke /admin/, membuat grup melalui menu Groups, lalu memasukkan akun yang dipilih ke grup tersebut melalui menu Users. View memeriksa keanggotaan grup menggunakan user.groups.filter(name="Editor").exists(). Editor tidak perlu diberi status staff atau superuser karena izin mengedit halaman portofolio diperiksa berdasarkan grup. Form registrasi juga tidak menyediakan pilihan role, sehingga pengguna tidak bisa menjadikan dirinya Editor. Pembatasan ini diterapkan pada Experience, Project, dan Education.

3. Fitur star Experience menggunakan ManyToManyField bernama starred_by yang terhubung ke model User. Relasi ini menyimpan pengguna yang memberikan star pada setiap Experience, dengan maksimal satu star per pengguna untuk satu item. Saat tombol ditekan, view memeriksa apakah pengguna sudah memberikan star. Jika sudah, relasinya dihapus; jika belum, relasinya ditambahkan. Permintaan harus memakai metode POST dan menyertakan {% csrf_token %}. Halaman menampilkan jumlah star dan status Star atau Unstar sesuai pengguna yang sedang login. Endpoint JSON dari Assignment 3 tetap berjalan, tetapi field yang dikirim dibatasi ke data publik agar relasi akun pemberi star tidak ikut ditampilkan.

4. Untuk menjalankan proyek, instal dependensi dan terapkan migrasi dari folder yang berisi manage.py:
python -m venv env
.\env\Scripts\python.exe -m pip install -r requirements.txt
.\env\Scripts\python.exe manage.py migrate
.\env\Scripts\python.exe manage.py createsuperuser
.\env\Scripts\python.exe manage.py runserver
Jika environment dan superuser sudah tersedia, keduanya tidak perlu dibuat lagi. Konfigurasi lokal memakai PRODUCTION=False pada .env. Website dapat dibuka melalui http://127.0.0.1:8000/. Pengujian dijalankan menggunakan .\env\Scripts\python.exe manage.py test main. Sebanyak 50 pengujian otomatis berhasil, termasuk pembatasan akses, star/unstar, CSRF, keamanan JSON, serta session dan cookie. Pengujian memakai database sementara sehingga tidak menghapus data asli.

### Assignment 5
1. Debouncing adalah teknik menunda pemanggilan fungsi sampai pengguna berhenti melakukan suatu aktivitas selama waktu tertentu. Pada pencarian Experience, saya memakai jeda 300 milidetik setelah input terakhir. Setiap kali pengguna mengetik lagi, timer sebelumnya dibatalkan dan dimulai ulang. Dengan begitu, browser tidak mengirim request untuk setiap huruf yang diketik. Ini mengurangi request ke server dan mencegah daftar berubah terlalu sering. Tombol Cari atau Enter tetap menjalankan pencarian langsung. Request sebelumnya juga dibatalkan dengan AbortController agar hasil pencarian lama tidak menggantikan hasil terbaru.

2. fetch() mengembalikan Promise, sehingga hasil request belum langsung tersedia saat fungsi dipanggil. await fetch() menunggu sampai respons tersedia sebelum baris berikutnya di dalam fungsi async dilanjutkan. Setelah itu, await response.json() menunggu isi respons selesai dibaca dan diubah menjadi data JavaScript. Proses menunggu ini tidak membekukan seluruh halaman. Kalau await dihilangkan tanpa penanganan Promise lain, variabel masih berisi Promise, bukan objek Response atau data JSON yang dibutuhkan, sehingga pemanggilan seperti response.json() bisa gagal. Alternatifnya adalah memakai .then(). Saya juga memeriksa response.ok karena status 400 atau 403 tidak otomatis membuat fetch() melempar error.

3. Cross-Site Scripting atau XSS adalah serangan yang membuat browser menjalankan kode berbahaya dari data yang seharusnya hanya ditampilkan. Contohnya, judul berisi tag img dengan atribut onerror bisa menjalankan JavaScript saat dimasukkan melalui innerHTML. Template Django secara default melakukan auto-escaping pada variabel, sedangkan data JSON yang dimasukkan lewat JavaScript tidak otomatis mendapat perlindungan tersebut. AJAX sendiri bukan penyebab XSS; risikonya muncul ketika data diperlakukan sebagai HTML tanpa pengamanan. Pada halaman Experience, saya memakai textContent untuk menampilkan judul, deskripsi, kategori, dan teks lain. ExperienceForm juga membersihkan judul serta deskripsi dengan strip_tags, menolak hasil yang kosong, dan memvalidasi URL melalui URLField. URL thumbnail dibatasi lagi ke http/https saat dirender. strip_tags hanya lapisan tambahan, bukan pengganti perlindungan saat menampilkan data lama maupun data baru.

#### Implementasi dan cara menjalankan
Bagian yang dilanjutkan adalah Experience dari Assignment 3 dan 4. Halaman /experience/ memuat kerangka halaman, lalu mengambil data dari /api/experience/. JSON berisi data publik, jumlah star, dan status star pengguna aktif, tanpa daftar akun pemberi star. Pencarian judul, loading/empty/error state, tombol Reset dan Coba lagi, modal tambah data, serta toast memakai JavaScript. Penambahan data dikirim ke /experience/add-ajax/ melalui POST dengan CSRF dan validasi ExperienceForm. Responsnya 201 untuk berhasil, 400 untuk input tidak valid, dan 403 untuk pengguna yang tidak berhak.

Hak akses tetap mengikuti Assignment 4: pengunjung bisa membaca, pengguna login bisa memberi star, Editor bisa mengedit, dan superuser bisa menambah, mengedit, serta menghapus. Halaman detail, edit, konfirmasi hapus, serta star/unstar tetap tersedia. Daftar tetap mengikuti kata pencarian yang aktif setelah data ditambahkan; data baru akan terlihat jika judulnya cocok.

Dari folder yang berisi manage.py, gunakan environment yang sudah tersedia:

```powershell
.\env\Scripts\python.exe -m pip install -r requirements.txt
.\env\Scripts\python.exe manage.py migrate
.\env\Scripts\python.exe manage.py check
.\env\Scripts\python.exe manage.py runserver
```

Konfigurasi lokal memakai PRODUCTION=False. Buka http://127.0.0.1:8000/experience/. Assignment 5 tidak mengubah model, sehingga tidak membutuhkan migrasi baru. Superuser dan grup Editor tetap menggunakan konfigurasi Assignment 4.

Pengujian otomatis:

```powershell
.\env\Scripts\python.exe manage.py test main
.\env\Scripts\python.exe manage.py makemigrations --check --dry-run
```

#### Penggunaan AI
Pengerjaan ini dibantu ChatGPT/Codex dengan PDF tugas, kode Tutorial 5, serta implementasi Assignment 3 dan 4 sebagai konteks. Bantuan mencakup view JSON, pencarian AJAX, modal, validasi dan perlindungan XSS/CSRF, penyesuaian tes, pengujian browser, serta penyusunan jawaban refleksi ini. Instruksi tambahan saya adalah mempertahankan fitur sebelumnya dan tidak menambahkan komentar kode baru.

Hasil AI diperiksa melalui pengujian Django dan browser, bukan hanya dari tampilannya. Pengujian tidak membuktikan bahwa semua kemungkinan bug sudah tertangani atau bahwa persyaratan waktu pengumpulan telah terpenuhi. Perbaikan selama sesi dilakukan oleh Codex dan tidak diklaim sebagai perbaikan manual mahasiswa. Ringkasan prompt, cakupan bantuan, dan hasil pemeriksaan tersedia di [log bantuan AI Assignment 5](docs/assignment5-ai-log.md).
