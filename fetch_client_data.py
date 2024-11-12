import requests
import json
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace with your API token

API_TOKEN = 'YOUR_API_TOKEN'
BASE_URL = 'https://api.workflow.prod.trulioo.com/export/v2/query'
CLIENT_LIST_URL = f'{BASE_URL}/clients?limit=50'
CLIENT_PROFILE_URL = f'{BASE_URL}/client/{{}}'

output_folder = 'client_profiles'
os.makedirs(output_folder, exist_ok=True)

def fetch_client_ids():
    client_ids = []
    page = 0

    while True:
        url = f"{CLIENT_LIST_URL}&page={page}"
        headers = {
            'Authorization': f'Bearer {API_TOKEN}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            ids_in_page = [item['id'] for item in data['data']]
            client_ids.extend(ids_in_page)

            logging.info(f"Fetched {len(ids_in_page)} client IDs from page {page}.")
            
            if data['last']:
                break
            page += 1
        else:
            logging.error(f"Failed to fetch client IDs on page {page}: {response.status_code}")
            break

    return client_ids

def fetch_data(client_id):
    url = CLIENT_PROFILE_URL.format(client_id)
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch data for client ID {client_id}: {response.status_code}")
        return None

client_ids = fetch_client_ids()
total_clients = len(client_ids)
logging.info(f"Total client IDs to process: {total_clients}")

for index, client_id in enumerate(client_ids, start=1):
    result = fetch_data(client_id)
    if result:
        with open(os.path.join(output_folder, f"{client_id}.json"), 'w') as json_file:
            json.dump(result, json_file, indent=4)
        logging.info(f"Data for client ID {client_id} saved as JSON.")
    
    progress = (index / total_clients) * 100
    logging.info(f"Progress: {index}/{total_clients} ({progress:.2f}%)")

logging.info("All profiles have been saved as JSON files.")
