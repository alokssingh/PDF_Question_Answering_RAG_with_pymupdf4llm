#from langchain.document_loaders import WebBaseLoader


'''
from langchain_community.document_loaders import WebBaseLoader
import time


def download_texts_and_metadata(web_links):
    web_links = web_links#[:4]
    texts = []
    metadatas = []
    for i in web_links:
        loader = WebBaseLoader([i])
        document = loader.load()
        for doc in document:
            texts.append(doc.page_content)
            metadatas.append(doc.metadata)
        time.sleep(8)
    return texts, metadatas


'''
'''
import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import time
import random
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# List of User-Agent strings
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/72.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
]

# Create a session and set retries with exponential backoff
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

def get_random_headers():
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    }
    return headers

def scrape_data_from_url(url):
    try:
        headers = get_random_headers()
        
        # Send a GET request to the URL with headers, skipping SSL verification
        response = session.get(url, headers=headers, timeout=10, verify=False)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the text from the page
            text = soup.get_text()

            # Extract metadata
            metadata = {}
            metadata['source'] = (url) 
            metadata['title'] = soup.title.string if soup.title else 'No title'
            metadata['description'] = (soup.find('meta', attrs={'name': 'description'}) or {}).get('content', 'No description')
            metadata['keywords'] = (soup.find('meta', attrs={'name': 'keywords'}) or {}).get('content', 'No keywords')

            return text, metadata
        else:
            print(f"Failed to retrieve {url} (Status code: {response.status_code})")
            return None, None
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
        print(f"An error occurred while retrieving {url}: {e}")
        return None, None


def download_texts_and_metadata(urls):
    texts = []
    metadatas = []
    for url in urls:
        text, metadata = scrape_data_from_url(url)
        if text and metadata:
            texts.append(text)
            metadatas.append(metadata)
        time.sleep(5)
    return texts, metadatas
'''


import os
import pandas as pd
from newsplease import NewsPlease
import signal
from functools import partial
import requests
import time


# Custom exception for timeout
class TimeoutException(Exception):
    pass

# Timeout handler
def timeout_handler(signum, frame):
    raise TimeoutException("Processing took too long")

def process_url_with_timeout(url, timeout=30):
    # Set the timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        # Set a timeout for the requests library as well
        article = NewsPlease.from_url(url, timeout=timeout)
        # If successful, cancel the alarm
        signal.alarm(0)
        return article
    except TimeoutException:
        print(f"Timeout occurred while processing URL: {url}")
        return None
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return None
    finally:
        # Ensure the alarm is canceled
        signal.alarm(0)

def download_texts_and_metadata(urls):
    texts = []
    metadatas = []

    for url in urls:
        if url.lower().endswith('.pdf'):
            print(f"Skipping PDF file: {url}")
            continue

        #print(f"Processing URL: {url}")
        article = process_url_with_timeout(url)

        if article:
            if article.maintext:
                metadatas.append({'processed_urls':url, 'titles':article.title if article.title else "No title", 'date_published':str(article.date_publish) if article.date_publish else "No Publish Date",'sources':article.source_domain if article.source_domain else "No Source Domain"})
                texts.append(article.maintext if article.maintext else "No main text")
    
    return texts, metadatas
            