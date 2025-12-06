# 📚 Analisis Data Perpustakaan & Sistem Pendukung Keputusan (DSS)

Selamat datang di proyek Analisis Data Perpustakaan. Proyek ini bertujuan untuk menggali wawasan mendalam dari data transaksi perpustakaan dan menyediakan sistem rekomendasi cerdas untuk pengadaan buku.

---

## 📋 Daftar Isi
1.  [Tentang Proyek](#-tentang-proyek)
2.  [Struktur Dataset](#-struktur-dataset)
3.  [Modul Analisis](#-modul-analisis)
4.  [Metodologi](#-metodologi)
5.  [Hasil & Visualisasi](#-hasil--visualisasi)
6.  [Cara Menjalankan](#-cara-menjalankan)

---

## 📖 Tentang Proyek

Sistem ini dirancang untuk membantu pustakawan dalam mengambil keputusan berbasis data. Dengan menggunakan teknik *Data Mining* dan *Decision Support System* (DSS), kami menjawab pertanyaan krusial seperti:
*   Buku apa yang paling diminati?
*   Buku apa yang sering dipinjam bersamaan? (Pola Asosiasi)
*   Buku mana yang harus segera diganti atau ditambah stoknya?

---

## 🗄️ Struktur Dataset

Analisis ini didukung oleh dataset relasional yang mencakup:

### 1. Data Buku
*   **`book_masters.csv`**: Katalog utama buku.
    *   `id`: Kode unik buku (Primary Key).
    *   `title`: Judul lengkap buku.
    *   `author`: Nama penulis.
    *   `categoryId`: Kode kategori buku.
*   **`book_items.csv`**: Inventaris fisik buku (eksemplar).
    *   `id`: Kode unik eksemplar.
    *   `masterId`: Referensi ke `book_masters`.
    *   `condition`: Kondisi fisik (`New`, `Good`, `Fair`, `Poor`).
    *   `status`: Status peminjaman (`Available`, `Borrowed`, `Lost`).
*   **`categorys.csv`**: Daftar kategori/genre.
    *   `id`: Kode kategori.
    *   `name`: Nama kategori (misal: *Fiksi*, *Sains*, *Sejarah*).

### 2. Data Transaksi
*   **`borrow_transactions.csv`**: Catatan peminjaman.
    *   `id`: Kode transaksi.
    *   `borrowDate`: Tanggal transaksi dilakukan.
*   **`borrow_details.csv`**: Rincian buku yang dipinjam.
    *   `borrowId`: Referensi ke transaksi.
    *   `bookItemId`: Referensi ke eksemplar buku yang dipinjam.

---

## 🔍 Modul Analisis

Proyek ini terdiri dari beberapa skrip Python yang masing-masing memiliki fokus analisis spesifik:

| Script | Deskripsi & Tujuan |
| :--- | :--- |
| **`analyze_book_popularity.py`** | **Analisis Popularitas**: Mengklasifikasikan buku ke dalam label **HOT** (Sangat Populer), **MODERATE**, **LOW**, dan **FLOP** berdasarkan frekuensi peminjaman. |
| **`analyze_top_books.py`** | **Top Charts**: Menghasilkan daftar 10 buku dengan jumlah peminjaman tertinggi sepanjang masa. |
| **`analyze_book_association.py`** | **Market Basket Analysis (Buku)**: Menemukan pola peminjaman antar buku. Contoh: *"Jika meminjam Buku A, 70% kemungkinan juga meminjam Buku B"*. |
| **`analyze_category_association.py`** | **Market Basket Analysis (Kategori)**: Menganalisis hubungan antar genre. Berguna untuk memahami preferensi lintas topik anggota perpustakaan. |
| **`dss_recommendation.py`** | **Sistem Rekomendasi (DSS)**: Memberikan saran aksi (Ganti/Beli Baru) berdasarkan kondisi fisik buku dan tingkat permintaannya. |

---

## 🧠 Metodologi

### 1. Association Rule Mining (Pola Asosiasi)
Kami menggunakan pendekatan *Market Basket Analysis* untuk menemukan hubungan antar item.
*   **Support**: Seberapa populer suatu kombinasi item.
*   **Confidence**: Seberapa kuat hubungan sebab-akibat (Jika A maka B).
*   **Lift**: Rasio ketergantungan. Nilai `Lift > 1` menunjukkan hubungan yang signifikan dan bukan kebetulan.

### 2. Weighted Scoring Model (DSS)
Untuk rekomendasi pengadaan buku, kami menggunakan model pembobotan sederhana namun efektif. Setiap buku dinilai dengan rumus:

$$ \text{Score} = (1.0 \times \text{BorrowCount}) + (10.0 \times \text{PoorCopies}) + (2.0 \times \text{FairCopies}) $$

**Penjelasan Bobot:**
*   **Kondisi Buruk (10.0)**: Prioritas tertinggi. Buku yang rusak (`Poor`) harus segera diganti untuk menjaga kualitas layanan.
*   **Kondisi Sedang (2.0)**: Prioritas menengah. Buku kondisi `Fair` perlu dipantau.
*   **Popularitas (1.0)**: Faktor pendukung. Buku yang rusak DAN populer akan mendapatkan skor sangat tinggi, menjadikannya prioritas utama pengadaan.

---

## 📊 Hasil & Visualisasi

Berikut adalah ringkasan visual dari hasil analisis data perpustakaan.

### 🏆 1. Buku Terlaris (Top 10)
Daftar buku yang menjadi favorit pemustaka.
![Top 10 Books](analysis/visualizations/top_10_books.png)

### 📈 2. Distribusi Status Buku
Gambaran umum koleksi perpustakaan berdasarkan tingkat aktivitasnya.
![Book Status Distribution](analysis/visualizations/book_status_distribution.png)

### 📚 3. Popularitas Kategori
Genre buku yang paling banyak dicari.
![Category Popularity](analysis/visualizations/category_popularity.png)

### 🕸️ 4. Jaringan Asosiasi (Buku & Kategori)
Visualisasi graf yang menunjukkan keterhubungan antar buku dan antar kategori. Ketebalan garis menunjukkan kekuatan hubungan (*Lift*).

**Asosiasi Buku:**
![Association Network](analysis/visualizations/association_network.png)

**Asosiasi Kategori:**
![Category Association Network](analysis/visualizations/category_association_network.png)

### 💡 5. Rekomendasi Pembelian (DSS)
Daftar prioritas pengadaan buku. Grafik ini menyoroti buku-buku yang paling mendesak untuk dibeli kembali.
![DSS Recommendations](analysis/visualizations/dss_top_recommendations.png)

---

## 🚀 Cara Menjalankan

Pastikan Anda telah menginstal Python dan library yang dibutuhkan (`pandas`, `matplotlib`, `seaborn`, `networkx`).

1.  **Jalankan Analisis**:
    ```bash
    python analysis/analyze_book_popularity.py
    python analysis/analyze_top_books.py
    python analysis/analyze_book_association.py
    python analysis/analyze_category_popularity.py
    python analysis/analyze_category_association.py
    python analysis/dss_recommendation.py
    ```

2.  **Generate Visualisasi**:
    ```bash
    python analysis/visualize_results.py
    ```

3.  **Lihat Hasil**:
    *   Data CSV: `analysis/output/`
    *   Gambar Grafik: `analysis/visualizations/`

---
*Dikembangkan untuk Proyek DSS Perpustakaan*
