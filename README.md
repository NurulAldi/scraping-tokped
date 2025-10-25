# E-Commerce Price Monitor

## Masalah Bisnis

Seorang pemilik toko online kecil di Tokopedia ingin tahu bagaimana **harga produk pesaingnya berubah setiap hari**, khususnya untuk kategori *headphone bluetooth*.  
Dengan informasi ini, ia bisa menentukan strategi harga yang lebih kompetitif — misalnya, menurunkan harga saat pasar sedang ramai diskon, atau menaikkan margin ketika kompetitor kehabisan stok.

Namun, masalahnya:
- Ia **tidak punya waktu** untuk memantau harga pesaing satu per satu.
- Tidak ada fitur bawaan Tokopedia yang menampilkan **riwayat harga kompetitor dari waktu ke waktu**.
- Ia butuh cara **otomatis dan terstruktur** untuk mengumpulkan serta menganalisis data harga pesaing setiap hari.

---

## Solusi Teknis

Proyek **Mata-Mata Harga E-Commerce** ini membangun *mini data pipeline* otomatis yang:

1. **Mengambil data produk headphone bluetooth dari Tokopedia** menggunakan Search Query API Tokopedia.
2. **Memproses dan membersihkan data** menggunakan Python (melalui notebook Jupyter).
3. **Menyimpan hasil bersih ke BigQuery** sebagai database historis yang bisa diakses dan dianalisis kapan pun.
4. (Opsional) **Menjalankan proses otomatis tiap pagi** dengan cron job atau GitHub Actions.

---

## Diagram Alur Data & Tools


![alt text](image\data-flow-diagram.png)



| Komponen | Fungsi | Tools |
|-----------|---------|--------|
| Data Source | Sumber data harga | **Tokopedia Search API** |
| Data Collection | Mengambil data mentah | **Python (Requests)** |
| Data Cleaning | Membersihkan dan menormalisasi data | **Jupyter Notebook (pandas, re)** |
| Data Storage | Menyimpan data historis | **Google BigQuery** |
| Automation | Menjalankan scraping terjadwal | **GitHub Actions** |

---

## 🔄 Pipeline Data

### **Alur Data (ETL Pipeline)**

### **1. Extract**
Mengambil data mentah dari **Tokopedia Search Query API** menggunakan `scrap.py`:
- **Query**: Headphone bluetooth dengan parameter pencarian terstruktur
- **Pagination**: Maksimal 5 halaman dengan 60 produk per halaman
- **Rate Limiting**: Jeda 2 detik antar request untuk menghindari blocking

| Field yang Diekstrak | Sumber API | Contoh Data |
|---------------------|------------|-------------|
| `name` | Product name | "Headphone Bluetooth JBL T450BT" |
| `price.text` | Formatted price | "Rp299.000" |
| `rating` | Product rating | 4.5 |
| `shop.name` | Store name | "JBL Official Store" |
| `shop.city` | Store location | "Jakarta Pusat" |
| `url` | Product URL | "https://tokopedia.com/..." |

**Output**: `data/raw/hasil_tokopedia_scrap.json`

### **2. Transform**
Proses pembersihan dan standarisasi menggunakan **Python (Pandas)** di `prep_data.ipynb`:
- **Pembersihan Harga**: Menghilangkan simbol "Rp", titik (`.`), dan koma (`,`) lalu konversi ke integer
- **Normalisasi Kolom**: Rename kolom menjadi format standar yang konsisten
- **Deduplication**: Menghapus duplikat berdasarkan kombinasi `nama_produk` dan `nama_toko`
- **Timestamp**: Menambahkan `timestamp_cleaned` untuk tracking kapan data diproses
- **Sorting**: Mengurutkan produk berdasarkan harga (ascending)

Standarisasi format kolom:
```text
nama_produk | harga | rating | nama_toko | lokasi_toko | url | timestamp_cleaned
```

| Proses | Before | After |
|--------|--------|-------|
| Price Cleaning | "Rp299.000" | 299000 |
| Column Rename | "Nama" → "nama_produk" | Konsisten snake_case |
| Deduplication | 300 rows | 120 rows |
| Timestamp | - | "2024-10-25 14:30:45" |

**Output**: `data/cleaned/tokopedia_headphone_cleaned.csv`

### **3. Load**
Memindahkan data hasil cleaning ke data warehouse **Google BigQuery** menggunakan `upload_to_bigquery.py`:
- **Authentication**: Service account JSON untuk koneksi aman ke BigQuery
- **Target**: Tabel di BigQuery dengan konfigurasi `WRITE_APPEND`
- **Batch Upload**: Menggunakan `load_table_from_dataframe()` untuk efisiensi
- **Data Validation**: Verifikasi sukses upload melalui job result

```python
# Konfigurasi BigQuery
client = bigquery.Client.from_service_account_json("service-account.json")
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
```