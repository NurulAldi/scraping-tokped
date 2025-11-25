import json
import boto3
import csv
from io import StringIO
from datetime import datetime
import re

# Initialize S3 client
s3_client = boto3.client('s3')

# Bucket names
SOURCE_BUCKET = 'raw-headphonebluetooth-data'
DESTINATION_BUCKET = 'clean-headphonebluetooth-data'

def clean_data(data):
    keywords_to_exclude = ['casing', 'silikon', 'cover', 'accessories', 'aksesoris', 'sarung', 'baterai headset', 'pembersih']
    
    cleaned_data = []
    seen_urls = set()
    
    for item in data:
        cleaned_item = {
            'nama_produk': item.get('Nama', ''),
            'harga': item.get('Harga', 0),
            'rating': item.get('Rating', ''),
            'nama_toko': item.get('Toko', ''),
            'lokasi_toko': item.get('Lokasi', ''),
            'url': item.get('URL', '')
        }
        
        nama_produk_lower = cleaned_item['nama_produk'].lower()
        if any(keyword in nama_produk_lower for keyword in keywords_to_exclude):
            continue
        
        if cleaned_item['url'] in seen_urls:
            continue
        seen_urls.add(cleaned_item['url'])
        
        cleaned_item['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cleaned_data.append(cleaned_item)
    
    cleaned_data.sort(key=lambda x: x['harga'])
    
    return cleaned_data

def lambda_handler(event, context):
    try:
        if 'Records' in event:
            file_key = event['Records'][0]['s3']['object']['key']
        else:
            response = s3_client.list_objects_v2(Bucket=SOURCE_BUCKET)
            if 'Contents' not in response:
                return {
                    'statusCode': 404,
                    'body': json.dumps('No files found in source bucket')
                }
            file_key = next((obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.json')), None)
            if not file_key:
                return {
                    'statusCode': 404,
                    'body': json.dumps('No JSON files found in source bucket')
                }
        
        print(f"Processing file: {file_key}")
        json_object = s3_client.get_object(Bucket=SOURCE_BUCKET, Key=file_key)
        json_content = json_object['Body'].read().decode('utf-8')
        data = json.loads(json_content)
        
        if not data or len(data) == 0:
            return {
                'statusCode': 400,
                'body': json.dumps('JSON file is empty')
            }
        
        original_count = len(data)
        print(f"Original data count: {original_count}")
        cleaned_data = clean_data(data)
        cleaned_count = len(cleaned_data)
        print(f"Cleaned data count: {cleaned_count}")
        
        if cleaned_count == 0:
            return {
                'statusCode': 400,
                'body': json.dumps('No data remaining after cleaning')
            }
        
        # Create CSV in memory
        csv_buffer = StringIO()
        fieldnames = ['nama_produk', 'harga', 'rating', 'nama_toko', 'lokasi_toko', 'url', 'timestamp']

        print("Writing CSV to memory")
        
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_data)
        
        output_key = file_key.replace('raw_hb_data_', 'cleaned_hb_data_').replace('.json', '.csv')
        
        s3_client.put_object(
            Bucket=DESTINATION_BUCKET,
            Key=output_key,
            Body=csv_buffer.getvalue(),
            ContentType='text/csv'
        )
        
        print(f"Successfully converted and cleaned {file_key} to {output_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'File converted and cleaned successfully',
                'source_file': file_key,
                'destination_file': output_key,
                'original_records': original_count,
                'cleaned_records': cleaned_count,
                'removed_records': original_count - cleaned_count
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
