from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import quote_plus # Construct the Google search URL


def perform_google_search(keywords):
    options = Options()
    options.add_argument('--headless=new')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    link_dict = {}
    print("in  [e]")
    print(keywords)

    for keyword in keywords:  # Adjust the range as needed
        print(keyword)
        links = []
        for page in range(1, 2):  # Search through 2 pages
            
            #url = f"https://www.google.com/search?q={keyword}&start={(page - 1) * 10}"
            start = page * 10
            keyword = quote_plus(keyword)
            url = f"{'https://www.bing.com/search'}?q={keyword}&start={start}"
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            search_results = soup.find_all('div', class_="yuRUbf")
            print(search_results)
            for result in search_results:
                link = result.a.get('href')
                print(link)
                links.append(link)
        link_dict[keyword] = links[:7]
        time.sleep(3)
    driver.quit()

    return link_dict