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
Assignment 5

1. Debouncing menunda pencarian sampai pengguna berhenti mengetik selama waktu tertentu. Di pencarian Experience, saya memasang jeda 300 milidetik, jadi browser tidak mengirim request setiap kali satu huruf diketik. Jumlah request dan beban server pun turun.

2. await membuat fungsi async menunggu hasil fetch() sebelum lanjut ke baris berikutnya. await response.json() menunggu respons selesai diubah menjadi data JavaScript. Tanpa await atau .then(), kode hanya memegang Promise, belum respons atau datanya, sehingga belum bisa dipakai langsung.

3. XSS adalah serangan yang menyisipkan kode berbahaya lewat data yang tampil di halaman. Template Django meng-escape data secara otomatis, tetapi JavaScript yang memasukkan data lewat innerHTML tidak melakukannya. Saya memakai textContent supaya data tampil sebagai teks biasa, dan menambahkan strip_tags di form sebagai lapisan perlindungan kedua.

### Assignment 6
 
1. REST adalah gaya arsitektur untuk layanan web, dan JSON hanyalah salah satu format representasi yang bisa dipakai di dalamnya. Aturan intinya: setiap data diperlakukan sebagai resource yang punya URL sendiri, dan aksi terhadapnya ditentukan oleh HTTP method. Endpoint seperti `/getExperience/` dan `/deleteExperience/` menaruh kata kerja di URL dan melayani semuanya lewat GET atau POST, jadi API yang mengembalikan JSON lewat endpoint semacam itu belum RESTful. API saya memakai satu URL `/api/v1/experience/<id>/` yang berperilaku berbeda menurut method, memakai status HTTP yang sesuai (201, 400, 403, 404, 204), dan tidak menyimpan state percakapan di server.
 
   PUT mengganti seluruh isi resource, sehingga field yang tidak dikirim dianggap kosong atau memicu error validasi. PATCH hanya mengubah field yang dikirim. Di proyek saya, `PUT /api/v1/experience/<id>/` tanpa `description` ditolak 400 karena field itu wajib. Tombol Edit pada kartu Experience karena itu memakai PATCH: pengguna yang hanya ingin mengganti judul tidak perlu mengirim ulang field lain, dan field lain itu harus tetap seperti semula. PUT cocok dipakai kalau formulir mengirim seluruh field sekaligus, misalnya saat mengganti isi satu entri secara penuh.
 
2. Serializer menerjemahkan dua arah: dari objek Django ke tipe data Python yang siap dijadikan JSON, dan dari JSON masuk ke objek yang sudah tervalidasi. Di Tutorial 05 saya menyusun dictionary manual lalu membungkusnya dengan `JsonResponse`; serializer memperbaiki empat hal dari cara itu.
 
   Validasi jadi terpusat. Aturan `validate_title` dan `validate_description` dengan `strip_tags` berlaku untuk POST, PUT, dan PATCH tanpa saya tulis ulang di tiap view. Daftar field eksplisit juga mencegah kebocoran data: dengan `fields` yang saya tulis satu per satu, relasi `starred_by` dan data akun tidak ikut terkirim, sedangkan pendekatan manual meloloskan keduanya begitu saya lupa menyaring. Field terhitung bisa saya buat read-only lewat `SerializerMethodField`, sehingga klien tidak dapat memalsukan `star_count` walaupun mengirimkannya di body. Terakhir, kode view saya jadi pendek dan seragam karena urusan representasi data tidak lagi bercampur dengan logika view.
 
3. Authentication memeriksa siapa pengirim request, sedangkan authorization memeriksa apakah pengirim itu boleh melakukan aksinya. Di proyek saya, `SessionAuthentication` mengenali pengguna dari cookie sesi, lalu `IsPortfolioOwnerOrEditorOrReadOnly` memutuskan izin aksinya. Pemisahan keduanya terlihat saat pengguna biasa berhasil terautentikasi tetapi tetap ditolak 403 ketika mencoba PATCH.
 
   Menyembunyikan tombol di template hanya merapikan tampilan. Siapa pun tetap bisa mengirim request ke `/api/v1/experience/<id>/` lewat curl, Postman, atau console browser, dan tombol yang tidak dirender tidak menghalangi hal itu. Pemeriksaan izin karena itu harus ada di server, satu-satunya titik yang tidak bisa dilewati klien. Saya membuktikannya lewat tes: akun biasa dan Editor yang menembak endpoint secara langsung tetap ditolak, dan tes memeriksa isi database untuk memastikan datanya tidak berubah, selain memeriksa status HTTP-nya.
 
4. `SessionAuthentication` mengandalkan cookie sesi, dan browser mengirim cookie itu otomatis ke domain asalnya pada setiap request, termasuk request yang dipicu halaman lain. Tanpa CSRF token, situs berbahaya cukup membuat halaman yang mengirim POST ke API saya: browser korban menyertakan cookie sesinya dan server menganggap request itu sah. CSRF token menutup celah tersebut karena nilainya harus dibaca dari cookie milik situs saya lalu dikirim balik di header `X-CSRFToken`, dan same-origin policy mencegah situs lain membacanya. API yang memakai token di header `Authorization` bebas dari masalah ini karena browser tidak mengirim token itu otomatis.
 
   `force_authenticate` melewati seluruh proses tersebut. Fungsi itu menempelkan objek user ke request tanpa cookie sesi dan tanpa pemeriksaan CSRF, sehingga tes yang memakainya tetap lulus walaupun perlindungan CSRF saya matikan. Jadi saya menambahkan tes terpisah dengan `APIClient(enforce_csrf_checks=True)` dan `.login()`, yang membuktikan request tanpa token ditolak 403 dan datanya tidak bertambah.