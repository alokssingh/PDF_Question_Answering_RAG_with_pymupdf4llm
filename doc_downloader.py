import os
import sys
import pandas as pd
from google_search import perform_google_search
from pdf_downloader import download_pdfs,download_pdfs_4_non_pdf_page
from text_downloader import download_texts_and_metadata
import os
from text_scrape import scrape_website
import requests
from search_engines import Bing

import re
    # Function for Separating pdf and non pdf links


def check_pdf_links(link_list):
    pdf_links = []
    non_pdf_links = []

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
    })

    for link in link_list:
        try:
            #print(f"Checking link: {link}")
            response = session.get(link, allow_redirects=True, timeout=10, stream=True)
            
            # Check if the response is valid
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                #print(f"Content-Type for {link}: {content_type}")
                
                # First, check if the Content-Type indicates a PDF
                if 'application/pdf' in content_type:
                    pdf_links.append(link)
                else:
                    # If Content-Type is ambiguous, read the first few bytes to check for %PDF signature
                    content_snippet = response.raw.read(4)
                    #print(f"Content snippet for {link}: {content_snippet}")
                    
                    if content_snippet == b"%PDF":
                        pdf_links.append(link)
                    else:
                        non_pdf_links.append(link)
            else:
                #print(f"Non-200 response for {link}: {response.status_code}")
                non_pdf_links.append(link)
        except requests.exceptions.RequestException as e:
            print(f"Error checking link {link}: {e}")
            non_pdf_links.append(link)

    return pdf_links, non_pdf_links





def main(file_path):

    if not os.path.exists(file_path):
        print("File does not exist.")
        return
    
    # Reading keywords from the data frame if you want to use your keyword either list all of them in a excel or assign it to keyword for ex keywords = ['petrochemical 1','petrochemical 2','petrochemical 3']

    df_petro = pd.read_excel(file_path)
    #df_petro['keyword_search'] = df_petro.iloc[:,1] + " data center of " +df_petro.iloc[:,2]+ " "+ " sustainable report pdf"
    
    #df_petro['keyword_search'] = df_petro.iloc[:,1] +"in "+county +" specification/techinical report pdf"
    #keywords = df_petro['keyword_search'].to_list()
    

    for rno in range(40,50):  #len(df_petro) it goes till the number of keywords you have
        
        data_center_name = df_petro.iloc[rno,1]
        data_provider_name = df_petro.iloc[rno,2]
        temp_loc = df_petro.iloc[rno,3].split(" ")
        county = " ".join([temp_loc[-2],temp_loc[-1]])
        county = re.sub(r'\n', ' ', county)
        #print(county)
        
        keywords = data_center_name + " datacenter of "+ data_provider_name + " technical specification  pdf"

        print("Looking for keyword = ", keywords)
        #link_dict = perform_google_search([keywords])    #perform_google_search_with_limit(keywords, 2, 5)#perform_google_search_with_limit(keywords, 2, 5)#perform_google_search
        engine = Bing()
        results = engine.search(keywords)
        links = results.links() 
        
        try:
            df_links = pd.DataFrame()
            df_links['Links'] = links
            df_links['keywords'] = keywords
        
            folder_path = "/Users/smit0225/Documents/Oxford/datacenter/clean_code/UK_data_centermap_spec/"+str(rno)+"_"+df_petro.iloc[rno,1]+ "_"+ df_petro.iloc[rno,2]
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            df_links.to_excel(folder_path+"/"+keywords+"_links.xlsx")


            #Extract PDF links    
            #pdf_links = df_links[df_links['Link'].str.endswith('.pdf')]['Link'].tolist()
            print("Separating pdf and non pdf links")
            print(df_links['Links'])
            pdf_links, non_pdf_links = check_pdf_links(df_links['Links'].tolist())
            #print(pdf_links)
            #print(non_pdf_links)
            
            print("download pdf start")           
            download_pdfs(pdf_links, folder_path)
            print("download pdf completed")
            
            
            #Extract non-PDF links
            #non_pdf_links = df_links[~df_links['Link'].str.endswith('.pdf')]['Link'].tolist()
            print("Trying PDF download for non pdf pages")
            download_pdfs_4_non_pdf_page(non_pdf_links, folder_path)

        except Exception as e:
            print("unfortunately  no links for this keyword")

        else:
            
            print("download text start")
            # Download text documents and metadata slowly
            texts, metadatas = download_texts_and_metadata(non_pdf_links)
            print("Number of links with text = ",len(texts))
            print("download text completed")
            
            # Create a DataFrame from texts and metadatas
            data = {'Text': texts, 'Metadata': metadatas}
            df = pd.DataFrame(data)
            # Save the DataFrame to a text file with escape character specified
            output_file = folder_path+"/"+keywords+'_link_output.xlsx'
            df.to_excel(output_file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <file_path>")
    else:
        file_path = sys.argv[1]
        main(file_path)


# Run using this command in terminal- python main1.py Copy_for_Google_search.xlsx