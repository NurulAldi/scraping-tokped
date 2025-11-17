
import pandas as pd
from datetime import datetime
import re

df = pd.read_json("data/raw/hasil_tokopedia_scrap.json")
print("Jumlah data mentah: ", len(df))

df.columns = ['nama_produk', 'harga', 'rating', 'nama_toko', 'lokasi_toko', 'url']

keywords_to_exclude = ['casing', 'silikon', 'cover', 'accessories', 'aksesoris', 'sarung', 'baterai headset', 'pembersih']
df = df[~df['nama_produk'].str.lower().str.contains('|'.join(keywords_to_exclude))]
print(f"Jumlah data setelah filter relevansi: {len(df)}")

before = len(df)
df = df.drop_duplicates(subset=['url'])
after = len(df)
print(f"Duplikat url dihapus: {before - after} baris")

df['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

df = df.sort_values(by='harga', ascending=True).reset_index(drop=True)


output_path = "data/cleaned/tokopedia_headphone_cleaned.csv"
df.to_csv(output_path, index=False)
print(f"Data bersih disimpan ke {output_path}")




