import os
import requests
import base64
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def clean_filename(url):
    # Remove query strings (everything after ?) when saving the filename
    path = urlparse(url).path
    return os.path.basename(path)


def download_file(url, folder, referer):
    filename = clean_filename(url)
    path = os.path.join(folder, filename)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/122.0.0.0 Safari/537.36",
        "Referer": referer
    }
    try:
        with requests.get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded: {url}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False


def save_base64_image(base64_string, folder, count):
    try:
        header, encoded = base64_string.split(",", 1)
        file_ext = header.split(";")[0].split("/")[1]
        filename = f"embedded_image_{count}.{file_ext}"
        path = os.path.join(folder, filename)

        decoded_data = base64.b64decode(encoded)

        if len(decoded_data) < 1024:
            print(f"Skipped a tiny useless base64 image (size: {len(decoded_data)} bytes)")
            return False

        with open(path, "wb") as f:
            f.write(decoded_data)

        print(f"Saved a real base64 image: {filename} (size: {len(decoded_data)} bytes)")
        return True
    except Exception as e:
        print(f"Failed to save base64 image: {e}")
        return False


def download_media(target_url):
    img_folder = "images"
    vid_folder = "videos"
    os.makedirs(img_folder, exist_ok=True)
    os.makedirs(vid_folder, exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(target_url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    base64_count = 0

    image_found = 0
    image_downloaded = 0
    video_found = 0
    video_downloaded = 0

    # Download images
    for img in soup.find_all("img"):
        img_url = (
                img.get("data-src") or
                img.get("data-original") or
                img.get("src")
        )
        if img_url:
            image_found += 1
            if img_url.startswith("data:image"):
                base64_count += 1
                if save_base64_image(img_url, img_folder, base64_count):
                    image_downloaded += 1
            else:
                full_url = urljoin(target_url, img_url)
                if download_file(full_url, img_folder, target_url):
                    image_downloaded += 1

    # Download videos
    for video in soup.find_all("video"):
        vid_url = video.get("src")
        if vid_url:
            video_found += 1
            full_url = urljoin(target_url, vid_url)
            if download_file(full_url, vid_folder, target_url):
                video_downloaded += 1
        else:
            for source in video.find_all("source"):
                source_url = source.get("src")
                if source_url:
                    video_found += 1
                    full_url = urljoin(target_url, source_url)
                    if download_file(full_url, vid_folder, target_url):
                        video_downloaded += 1

    # Final report
    print("\n--- Download Summary ---")
    print(f"Images Found: {image_found}")
    print(f"Images Downloaded: {image_downloaded}")
    print(f"Videos Found: {video_found}")
    print(f"Videos Downloaded: {video_downloaded}")


if __name__ == "__main__":
    target = input("Enter the target URL: ").strip()
    download_media(target)

