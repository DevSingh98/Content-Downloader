# Content-Downloader

#### 🖥️ Website Media Downloader

A powerful Python script that **downloads images and videos** from a given website URL.  
Handles regular media URLs, lazy-loaded images, and embedded base64 images.

## 🔥 Features
- Downloads:
  - Images (`.jpg`, `.jpeg`, `.png`, `.gif`, etc.)
  - Videos (`.mp4`, `.webm`, etc.)
- Detects and downloads:
  - Lazy-loaded images (`data-src`, `data-original`, etc.)
  - Embedded base64 images
- Saves files into structured folders (`images/` and `videos/`)
- Skips tiny base64 images to avoid useless downloads
- User-Agent spoofing and Referer headers for better compatibility
- Detailed download summary report

## 🛠️ Technologies Used
- Python 3
- Requests
- BeautifulSoup4 (bs4)
- urllib
- base64

## 🚀 How to Use
1. Clone the repository:
   ```bash
   git clone https://github.com/Devsingh98/Content-Downloader.git
   cd Content-Downloader
   ```

2. Install the required packages:
   ```bash
   pip install requests beautifulsoup4
   ```

3. Run the script:
   ```bash
   python download_media.py
   ```

4. Enter the URL when prompted.

## 📂 Output Structure
```
/Content-Downloader/
  ├── images/
  │    ├── image1.jpg
  │    ├── embedded_image_1.png
  │    └── ...
  ├── videos/
  │    ├── video1.mp4
  │    └── ...
```

## 🧠 How It Works
- Fetches the page content using a browser-like User-Agent.
- Parses the HTML with BeautifulSoup.
- Looks for:
  - `<img>` tags and sources (`src`, `data-src`, `data-original`)
  - `<video>` and `<source>` tags
- Automatically resolves relative URLs using `urljoin`.
- Downloads files in binary mode with chunking to prevent memory overload.
- Decodes and saves valid base64 images larger than 1 KB.

## ⚡ Notes
- This script **does not** recursively follow links across multiple pages.
- Websites with strong anti-scraping measures may block requests.
- Always ensure you have permission to download website content.

## 📈 Future Improvements
- Add recursive scraping for deeper download
- Multi-threaded downloads for faster performance
- Add support for additional file types



