# This code is scrapping text from the open source website using newsplease

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
            
