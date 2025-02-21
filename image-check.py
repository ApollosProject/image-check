import argparse
import csv
import xml.etree.ElementTree as ET
from io import BytesIO

import av
import requests
from PIL import Image
from tqdm import tqdm

parser = argparse.ArgumentParser(description="verify image URLs in a CSV file")
parser.add_argument("csv_file", type=str, help="the CSV file to verify")

args = parser.parse_args()


csv_file = args.csv_file
urls = []
with open(csv_file, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        urls.append(row["url"])


def is_valid_avif(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        # Check Content-Type
        if "image/avif" not in response.headers.get("Content-Type", ""):
            return False

        # Attempt to decode AVIF using PyAV
        with av.open(BytesIO(response.content), mode="r") as container:
            for frame in container.decode(video=0):
                if frame is not None:
                    return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def is_valid_svg(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        # Check Content-Type
        if "image/svg+xml" not in response.headers.get("Content-Type", ""):
            return False

        # Parse XML to check validity
        ET.fromstring(response.text)
        return True
    except Exception as e:
        print(e)
        return False


def is_valid_image(url):
    try:
        response = requests.get(url, stream=True, timeout=5)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        if "image/svg+xml" in content_type:
            return is_valid_svg(url)
        elif "image/avif" in content_type:
            return is_valid_avif(url)
        elif "image" in content_type:
            Image.open(BytesIO(response.content)).verify()
            return True
        else:
            print(f"Unsupported Content-Type: {content_type}, URL: {url}")
    except Exception as e:
        print(f"Error: {e}")
        return False

    return False


# verify the images are valid
invalid_images = []
for url in tqdm(urls):
    if not is_valid_image(url):
        invalid_images.append(url)
print("")
print("Invalid images:")
print("\n".join(invalid_images))
