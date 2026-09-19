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