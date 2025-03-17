import requests
from tqdm import tqdm
import argparse
from pathlib import Path

def download_zenodo_file(record_id, filename, destination, access_token=None):
    """
    Downloads a specific file from a Zenodo record with a progress bar.

    Parameters:
    - record_id (str): The Zenodo record ID.
    - filename (str): The exact name of the file to download.
    - destination (str): The local path where the file will be saved.
    - access_token (str, optional): Your Zenodo access token for restricted records.

    Returns:
    - None
    """
    base_url = f"https://zenodo.org/api/records/{record_id}"
    headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

    # Fetch the record metadata
    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    record = response.json()

    # Find the file in the record's files
    file_info = next((f for f in record["files"] if f["key"] == filename), None)
    if not file_info:
        raise FileNotFoundError(f"File '{filename}' not found in record '{record_id}'.")

    # Download the file with a progress bar
    download_url = file_info["links"]["self"]
    with requests.get(download_url, headers=headers, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        chunk_size = 1024 * 1024
        with open(destination, "wb") as f, tqdm(
            total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc=filename
        ) as progress_bar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                progress_bar.update(len(chunk))

    print(f"\nFile '{filename}' has been downloaded to '{destination}'.")
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o','--out_path', type=str)
    
    args = parser.parse_args()
    
    record_id = "15040443"  # Replace with your Zenodo record ID
    filename = ['config.zip', "test_dataset.h5"]  # Replace with the exact filename you wish to download
    for file in filename:
        destination = Path(args.out_path) / file  # Replace with your desired save path
        download_zenodo_file(record_id, file, destination)
