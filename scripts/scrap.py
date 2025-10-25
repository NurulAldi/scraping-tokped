import requests
import json
import time # Buat ngasih jeda

url = "https://gql.tokopedia.com/graphql/SearchProductV5Query"

# Salin header dari file lo, bikin jadi dictionary
headers = {
    "accept": "*/*",
    "content-type": "application/json",
    "referer": "https://www.tokopedia.com/",
    # Tambahin User-Agent, X-Source, X-Tkpd-Lite-Service, dll. dari file header lo
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36", # Contoh, ganti pakai punya lo
    "x-source": "tokopedia-lite",
    "x-tkpd-lite-service": "zeus",
    "x-dark-mode": "false",
    "x-price-center": "true",
    "x-device": "dektop-0.0",
    "x-version": "8a39727"
}

# Salin payload dari file lo
base_payload = [
  {
    "operationName": "SearchProductV5Query",
    "variables": {
      # Ini string params awal buat halaman 1
      "params": "device=desktop&enter_method=normal_search&l_name=sre&navsource=&ob=23&page=1&q=headphone%20bluetooth&related=true&rows=60&safe_search=false&sc=&scheme=https&shipping=&show_adult=false&source=search&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&st=product&start=0&topads_bucket=true&unique_id=05c09e3dab5a94813d4fc6c24d2aca19&user_addressId=&user_cityId=176&user_districtId=2274&user_id=&user_lat=&user_long=&user_postCode=&user_warehouseId=&variants=&warehouses=" # Ganti unique_id kalo perlu
    },
    "query": "query SearchProductV5Query($params: String!) { searchProductV5(params: $params) { header { totalData responseCode keywordProcess keywordIntention componentID isQuerySafe additionalParams backendFilters meta { dynamicFields __typename } __typename } data { totalDataText banner { position text applink url imageURL componentID trackingOption __typename } redirection { url __typename } related { relatedKeyword position trackingOption otherRelated { keyword url applink componentID products { oldID: id id: id_str_auto_ name url applink mediaURL { image __typename } shop { oldID: id id: id_str_auto_ name city tier __typename } badge { oldID: id id: id_str_auto_ title url __typename } price { text number __typename } freeShipping { url __typename } labelGroups { position title type url styles { key value __typename } __typename } rating wishlist ads { id productClickURL productViewURL productWishlistURL tag __typename } meta { oldWarehouseID: warehouseID warehouseID: warehouseID_str_auto_ componentID __typename } __typename } __typename } __typename } suggestion { currentKeyword suggestion query text componentID trackingOption __typename } ticker { oldID: id id: id_str_auto_ text query applink componentID trackingOption __typename } violation { headerText descriptionText imageURL ctaURL ctaApplink buttonText buttonType __typename } products { oldID: id id: id_str_auto_ ttsProductID name url applink mediaURL { image image300 videoCustom __typename } shop { oldID: id id: id_str_auto_ ttsSellerID name url city tier __typename } stock { ttsSKUID __typename } badge { oldID: id id: id_str_auto_ title url __typename } price { text number range original discountPercentage __typename } freeShipping { url __typename } labelGroups { position title type url styles { key value __typename } __typename } labelGroupsVariant { title type typeVariant hexColor __typename } category { oldID: id id: id_str_auto_ name breadcrumb gaKey __typename } rating wishlist ads { id productClickURL productViewURL productWishlistURL tag __typename } meta { oldParentID: parentID parentID: parentID_str_auto_ oldWarehouseID: warehouseID warehouseID: warehouseID_str_auto_ isImageBlurred isPortrait __typename } __typename } __typename } __typename } }\n" # String query panjang
  }
]

semua_produk = []
halaman_sekarang = 1
jumlah_produk_per_halaman = 60
total_produk_didapat = 0
maks_halaman = 5 

while True:
    print(f"Mengambil halaman {halaman_sekarang}...")
    try:
        params_sekarang = base_payload[0]['variables']['params']
        params_sekarang = params_sekarang.replace(f"page={halaman_sekarang-1}", f"page={halaman_sekarang}") # Ganti page
        start_sebelumnya = (halaman_sekarang - 2) * jumlah_produk_per_halaman
        start_sekarang = (halaman_sekarang - 1) * jumlah_produk_per_halaman
        params_sekarang = params_sekarang.replace(f"start={start_sebelumnya}", f"start={start_sekarang}") # Ganti start

        payload_sekarang = json.loads(json.dumps(base_payload)) # Deep copy biar gak ngubah base_payload
        payload_sekarang[0]['variables']['params'] = params_sekarang

        # Kirim request
        response = requests.post(url, headers=headers, json=payload_sekarang)
        response.raise_for_status() # Cek kalo ada error HTTP (4xx atau 5xx)

        data = response.json()

        # Cek struktur data (bisa beda dikit kadang)
        if isinstance(data, list):
            data = data[0] # Ambil elemen pertama kalo responsnya list

        # Ekstrak produk dari halaman ini
        produk_di_halaman = data['data']['searchProductV5']['data']['products']

        if not produk_di_halaman: # Kalo udah gak ada produk, berhenti
            print("Tidak ada produk lagi.")
            break

        print(f"Dapet {len(produk_di_halaman)} produk.")
        # Ambil data yang lo mau dari tiap produk
        for produk in produk_di_halaman:
            nama = produk.get('name')
            harga = produk.get('price', {}).get('text')
            rating = produk.get('rating')
            toko = produk.get('shop', {}).get('name')
            kota_toko = produk.get('shop', {}).get('city')
            url_produk = produk.get('url')
            # Ambil data lain kalo perlu

            semua_produk.append({
                'Nama': nama,
                'Harga': harga,
                'Rating': rating,
                'Toko': toko,
                'Lokasi': kota_toko,
                'URL': url_produk
            })
            total_produk_didapat += 1

        # Cek total data dari header (buat tau kapan harus berhenti)
        total_data_keseluruhan = data['data']['searchProductV5']['header']['totalData']
        print(f"Total produk keseluruhan: {total_data_keseluruhan}")

        # Berhenti kalo udah capai batas halaman atau udah semua produk
        if halaman_sekarang >= maks_halaman or total_produk_didapat >= total_data_keseluruhan:
            print("Mencapai batas halaman atau semua produk sudah diambil.")
            break

        halaman_sekarang += 1
        # Kasih jeda biar sopan dan gak diblokir
        time.sleep(2) # Jeda 2 detik, sesuaikan kalo perlu

    except requests.exceptions.RequestException as e:
        print(f"Error request: {e}")
        break
    except KeyError as e:
        print(f"Struktur JSON respons berubah atau tidak sesuai, error di key: {e}")
        print("Respons:", json.dumps(data, indent=2)) # Cetak respons buat debug
        break
    except Exception as e:
        print(f"Error lain: {e}")
        break

print(f"\nTotal produk yang berhasil di-scrape: {len(semua_produk)}")

# Di sini lo bisa simpen data `semua_produk` ke CSV atau JSON
# Contoh simpen ke JSON
with open('hasil_tokopedia_scrap.json', 'w', encoding='utf-8') as f:
    json.dump(semua_produk, f, ensure_ascii=False, indent=4)
print("Data disimpan ke hasil_tokopedia.json")

# Contoh simpen ke CSV
# import pandas as pd
# df = pd.DataFrame(semua_produk)
# df.to_csv('hasil_tokopedia.csv', index=False, encoding='utf-8')
# print("Data disimpan ke hasil_tokopedia.csv")