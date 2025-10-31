import os
import requests
from io import BytesIO
from PIL import Image

# --- Configuration ---
API_URL = "https://devimmerz.novactech.in/immerz/get-selfies"
OUTPUT_BASE_DIR = r'C:\Users\k1193\Music\augument'

# --- Utility Functions ---
def download_and_save_image(url, output_path):
    """Download image from URL and save it to the specified path."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Use PIL to open and save the image
        img = Image.open(BytesIO(response.content))
        img.save(output_path)
        return True
    except Exception as e:
        print(f"❌ Failed to download or save {url} to {output_path}: {e}")
        return False

# --- Main ---
def download_all_images():
    """Fetches user data and downloads all images to the target directory."""
    print(f"Attempting to fetch data from API: {API_URL}")
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Failed to fetch data from API: {e}")
        return

    if not data:
        print("❌ No images found from API.")
        return

    # Create the target directory
    os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)
    print(f"✓ Output folder '{OUTPUT_BASE_DIR}' ensured to exist.")

    print("\n⬇️ Starting image download for all users...\n")
    download_count = 0

    for idx, user_data in enumerate(data, 1):
        user_name = user_data.get("name", f"user{idx}")
        img_url = user_data.get("file_path")
        
        # Determine the filename and path
        # Extract the original file extension, or default to .jpg
        extension = os.path.splitext(img_url.split('/')[-1])[1] or '.jpg'
        filename = f"{user_name}_{idx}{extension}"
        output_path = os.path.join(OUTPUT_BASE_DIR, filename)

        print(f"[{idx}] Downloading '{user_name}' image from {img_url}")

        if download_and_save_image(img_url, output_path):
            print(f"  ✓ Saved as: {filename}")
            download_count += 1
        else:
            print(f"  ❌ Skipping {user_name} (download failed)")

    print("=" * 70)
    print(f"🎉 Completed! Total images downloaded: {download_count}")
    print(f"Images are saved in the '{OUTPUT_BASE_DIR}' directory.")
    print("=" * 70)

# --- Entry Point ---
if __name__ == "__main__":
    download_all_images()