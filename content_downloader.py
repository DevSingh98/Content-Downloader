import os
import requests
import base64
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed


def clean_filename(url):
    path = urlparse(url).path
    return os.path.basename(path)


def download_file(url, folder, referer):
    filename = clean_filename(url) or "unnamed"
    path = os.path.join(folder, filename)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/122.0.0.0 Safari/537.36",
        "Referer": referer
    }
    try:
        total_bytes = 0
        with requests.get(url, stream=True, headers=headers, timeout=20) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_bytes += len(chunk)
        print(f"Downloaded: {url} ({total_bytes/1024:.2f} KB)")
        return True, total_bytes
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False, 0


def save_base64_image(base64_string, folder, count):
    try:
        header, encoded = base64_string.split(",", 1)
        file_ext = header.split(";")[0].split("/")[1]
        filename = f"embedded_image_{count}.{file_ext}"
        path = os.path.join(folder, filename)

        decoded_data = base64.b64decode(encoded)

        if len(decoded_data) < 1024:
            print(f"Skipped tiny base64 image ({len(decoded_data)} bytes)")
            return False, 0

        with open(path, "wb") as f:
            f.write(decoded_data)

        print(f"Saved base64 image: {filename} ({len(decoded_data)/1024:.2f} KB)")
        return True, len(decoded_data)
    except Exception as e:
        print(f"Failed to save base64 image: {e}")
        return False, 0


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
        response = requests.get(target_url, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    base64_count = 0

    total_size = 0
    image_found = 0
    image_downloaded = 0
    video_found = 0
    video_downloaded = 0

    start_time = time.time()
    tasks = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Collect image tasks
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
                    ok, size = save_base64_image(img_url, img_folder, base64_count)
                    if ok:
                        image_downloaded += 1
                        total_size += size
                else:
                    full_url = urljoin(target_url, img_url)
                    tasks.append(("image", executor.submit(download_file, full_url, img_folder, target_url)))

        # Collect video tasks
        for video in soup.find_all("video"):
            vid_url = video.get("src")
            if vid_url:
                video_found += 1
                full_url = urljoin(target_url, vid_url)
                tasks.append(("video", executor.submit(download_file, full_url, vid_folder, target_url)))
            else:
                for source in video.find_all("source"):
                    source_url = source.get("src")
                    if source_url:
                        video_found += 1
                        full_url = urljoin(target_url, source_url)
                        tasks.append(("video", executor.submit(download_file, full_url, vid_folder, target_url)))

        # Wait for all downloads
        for ftype, future in tasks:
            ok, size = future.result()
            if ok:
                total_size += size
                if ftype == "image":
                    image_downloaded += 1
                else:
                    video_downloaded += 1

    elapsed = time.time() - start_time

    print("\n--- Download Summary ---")
    print(f"Images Found: {image_found}")
    print(f"Images Downloaded: {image_downloaded}")
    print(f"Videos Found: {video_found}")
    print(f"Videos Downloaded: {video_downloaded}")
    print(f"Total size downloaded: {total_size/1024/1024:.2f} MB")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Average speed: {(total_size/1024/1024) / elapsed:.2f} MB/s")


if __name__ == "__main__":
    target = input("Enter the target URL: ").strip()
    download_media(target)
