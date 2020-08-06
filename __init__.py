import datetime
import logging
import io, os, uuid
import requests
import azure.functions as func
import urllib3
from urllib3 import request
import json
import pandas as pd
import certifi
from twilio.rest import Client
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def main(mytimer: func.TimerRequest) -> None:
    # Timer Trigger Function Start

    # Define UTC timestamp for logging purpose
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    # Configure https certification handle
    http = urllib3.PoolManager(
       cert_reqs='CERT_REQUIRED',
       ca_certs=certifi.where())

    # Getting current number of confirmed COVID-19 cases in particular Hong Kong district from HK Gov Open Data API
    url = "https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Fbuilding_list_eng.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%2C%22filters%22%3A%5B%5B1%2C%22ct%22%2C%5B%22Tai%20Po%22%5D%5D%5D%7D"
    r = http.request("GET", url)
    data = json.loads(r.data.decode('utf-8'))
    df = pd.DataFrame(data, columns=["District","Building name","Last date of residence of the case(s)","Related probable/confirmed cases"])
    df_count = df.shape[0]

    # Download previously state file from Azure Blob Storage
    response = requests.get("https://minionsbotstore.blob.core.windows.net/public/export_df_old.csv")
    file_object = io.StringIO(response.content.decode('utf-8'))
    download_temp = pd.read_csv(file_object)
    download_temp.to_csv("/tmp/export_df_old.csv")
    df_old = pd.read_csv("/tmp/export_df_old.csv")
    df_old_count = df_old.shape[0]

    # Logging current and previously number of confirmed COVID-19 cases
    logging.info('Count of case 3 hours ago %s', df_old_count)
    logging.info('Count of current case %s', df_count)

    # Compare current vs previously state case number is equal or not
    df_div = df_count is df_old_count

    # Saving current state to archive
    df.to_csv (r'/tmp/export_df_old.csv', index = False, header=True)
    # Define Blob Storage connection string
    connect_str = 'PLEASE_OBTAIN_AND_ENTER_YOUR_OWN_AZURE_BLOB_STORAGE_CONNECTION_STRING'
    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    # Define Blob Storage container name
    container_name = "public"
    # Create a file in local Documents directory to upload and download
    local_path = "/tmp/"
    local_file_name = "export_df_old" + ".csv"
    upload_file_path = os.path.join(local_path, local_file_name)
    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)
    print("\nUploading to Blob Storage as blob:\n\t" + local_file_name)
    # Upload the created file
    with open(upload_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    logging.info('File has been upload to Blob Storage at %s', utc_timestamp)

    # Define Twilio client with authentication
    account_sid = 'PLEASE_OBTAIN_AND_ENTER_YOUR_OWN_TWILIO_ACCOUNT_ID'
    auth_token = 'PLEASE_OBTAIN_AND_ENTER_YOUR_OWN_TWILIO_ACCOUNT_KEY'
    client = Client(account_sid, auth_token)

    # Send WhatsApp alert message if current vs previously state case number does not match
    if df_div == False:
        message = client.messages.create(
                                    from_='whatsapp:+14155238886',
                                    body='New COVID-19 case found in Tai Po district, time check at ' + utc_timestamp + '.',
                                    to='whatsapp:PLEASE_ENTER_WHATSAPP_PHONE_NUMBER_FOR_ALERT_RECEIVE'
                                )
        print(message.sid)
        print("New COVID-19 case found in Tai Po district, time check at " + utc_timestamp + ".")
        logging.info('New COVID-19 case found in Tai Po district at %s.', utc_timestamp)
    else:
        print("No new COVID-19 case found in Tai Po district, time check at " + utc_timestamp + ".")
        logging.info('No new COVID-19 case found in Tai Po district %s.', utc_timestamp)

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    # Timer Trigger Function End



