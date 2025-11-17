from google.cloud import bigquery
import pandas as pd

df = pd.read_csv("data/cleaned/tokopedia_headphone_cleaned.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

client = bigquery.Client.from_service_account_json("service-account.json")

table_id = "marketing-data-pipeline-475911.tokped_scrap.headphone_bluetooth"

job = client.load_table_from_dataframe(
    df,
    table_id,
    job_config=bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND"
    ),
)

job.result()
print(f"Data berhasil diupload ke {table_id}")
