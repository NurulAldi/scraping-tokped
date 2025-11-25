from dotenv import load_dotenv
import os
import boto3
from datetime import datetime

# Load environment variables dari .env
load_dotenv()

# Inisialisasi client S3
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

tanggal = datetime.now().strftime("%m_%d_%Y")
bucket_name = 'raw-headphonebluetooth-data'
local_file = f'data/raw/hasil_tokopedia_scrap_{tanggal}.json'


s3_key = f'raw_hb_data_{tanggal}.json'

try:
    s3.upload_file(local_file, bucket_name, s3_key)
    print(f"File {local_file} berhasil diupload ke s3://{bucket_name}/{s3_key}")
except Exception as e:
    print("Gagal upload file ke S3:")
    print(e)