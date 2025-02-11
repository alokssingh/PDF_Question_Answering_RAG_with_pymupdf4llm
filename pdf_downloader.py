import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote


def download_pdfs(pdf_links, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"})
    for index, pdf_url in enumerate(pdf_links):
        #filename = pdf_url.split("/")[-1]
        #filepath = os.path.join(folder_path, filename)
        filename = os.path.basename(urlparse(pdf_url).path)
        filename = unquote(filename)
        filepath = os.path.join(folder_path, filename)
        try:
            response = session.get(pdf_url,  stream=True)
            response.raise_for_status()  # Check if the request was successful
            # Print status and content type for debugging
            #print(f"Status Code: {response.status_code}, Content-Type: {response.headers.get('Content-Type', '')}")

            if 'application/pdf' in response.headers.get('Content-Type', ''):
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            #print(f"PDF downloaded successfully as {filepath}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download PDF from {pdf_url}")
        time.sleep(5)


def download_pdfs_4_non_pdf_page(pdf_links, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    for index, url in enumerate(pdf_links):
        try:
            # Fetch the page content
            response = requests.get(url)
            response.raise_for_status()  # Check if request was successful

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all iframe and embed tags
            pdf_links = []
            for tag in soup.find_all(["iframe", "embed"]):
                src = tag.get("src")
                if src and src.endswith(".pdf"):
                    pdf_links.append(src)
            filename = url.split("/")[-1]
            filepath = os.path.join(folder_path, filename)
            if pdf_links:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("PDF is embedded in the page. Links found:", filepath)
                
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch the page: {e}")
    time.sleep(5)