# i need to take in a CSV as a command line argument and output a list of the URLs in an array
import argparse
import csv
from io import BytesIO

import requests
from PIL import Image

parser = argparse.ArgumentParser(description="verify image URLs in a CSV file")
parser.add_argument("csv_file", type=str, help="the CSV file to verify")

args = parser.parse_args()

csv_file = args.csv_file
urls = []
with open(csv_file, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        urls.append(row["url"])


def is_valid_image(url):
    try:
        # Send a request to the URL
        response = requests.get(url, stream=True, timeout=5)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        # Check the Content-Type header
        if "image" not in response.headers.get("Content-Type", ""):
            return False

        # Try opening the image using PIL
        Image.open(BytesIO(response.content)).verify()  # Verify does not decode image
        return True
    except Exception:
        return False


# verify the images are valid
for url in urls:
    if not is_valid_image(url):
        print(f"{url} is not a valid image")
