import requests
import json
import csv
import os

# -------------------------------
# CONFIGURE THESE
# -------------------------------
API_URL = "https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/40381/hscard"
API_KEY = "72e1bd568fmshd84b1b4352c0d19p134fe2jsndee496cdf794"
API_HOST = "cricbuzz-cricket.p.rapidapi.com"
OUTPUT_FOLDER = "output"
# -------------------------------

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def fetch_api_data():
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {response.text}")
        return None
    except Exception as err:
        print(f"Other error occurred: {err}")
        return None

    try:
        return response.json()
    except json.JSONDecodeError:
        print("Failed to parse JSON response")
        return None

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")

def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten nested dictionary: 
    {"player": {"name": "A", "runs": 50}} -> {"player_name": "A", "player_runs": 50}
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert list of simple items to string, skip nested lists
            if all(not isinstance(i, (dict, list)) for i in v):
                items.append((new_key, ','.join(map(str, v))))
            else:
                # Skip complex nested lists
                items.append((new_key, json.dumps(v)))
        else:
            items.append((new_key, v))
    return dict(items)

def save_dict_list_to_csv(dict_list, filename):
    if not dict_list:
        print(f"No data to save for {filename}")
        return

    # Flatten each dictionary
    flat_list = [flatten_dict(d) for d in dict_list]

    # Collect all unique headers
    headers = set()
    for d in flat_list:
        headers.update(d.keys())
    headers = list(headers)

    # Write CSV
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(flat_list)

    print(f"CSV saved: {filename}")

def extract_lists(data, parent_key="root"):
    """
    Recursively find all lists of dictionaries in the JSON and save them to CSV.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            extract_lists(value, parent_key=key)
    elif isinstance(data, list):
        if data and all(isinstance(item, dict) for item in data):
            filename = os.path.join(OUTPUT_FOLDER, f"{parent_key}.csv")
            save_dict_list_to_csv(data, filename)
        else:
            for i, item in enumerate(data):
                extract_lists(item, parent_key=f"{parent_key}_{i}")

def main():
    print("Fetching data from API...")
    data = fetch_api_data()
    if data:
        save_json(data, os.path.join(OUTPUT_FOLDER, "api_response.json"))
        extract_lists(data)
    else:
        print("Failed to fetch API data.")

if __name__ == "__main__":
    main()
