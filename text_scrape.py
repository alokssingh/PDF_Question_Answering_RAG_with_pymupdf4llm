import requests
from bs4 import BeautifulSoup


def scrape_website(urls):
    texts = []
    metadatas = []
    texts = []
    metadatas = []
    # print(len(documents))
    for url in urls:
        # Fetch the webpage content
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all text from the webpage
            text = soup.get_text()

            # return text
            texts.append(text)
            metadatas.append(url)
        else:
            print("Failed to fetch the webpage:", response.status_code)
            texts.append(None)
            metadatas.append(url)

    return texts, metadatas

