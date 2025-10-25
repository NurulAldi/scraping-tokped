from google.cloud import bigquery
import pandas as pd

df = pd.read_csv("data/cleaned/tokopedia_headphone_cleaned.csv")

client = bigquery.Client.from_service_account_json("marketing-data-pipeline-475911-d068969bbb6e.json")

table_id = "service-account.json"

job = client.load_table_from_dataframe(
    df,
    table_id,
    job_config=bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND"
    ),
)

job.result()
print(f"Data berhasil diupload ke {table_id}")
