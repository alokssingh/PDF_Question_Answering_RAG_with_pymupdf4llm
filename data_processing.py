import pandas as pd


def process_data(file_path):
    df_petro = pd.read_excel(file_path)
    df_petro['keyword_search'] = ' capacity/owner/feedstock of petrochemical plant ' + df_petro['Plant_name'].astype(str) + 'whose owner is ' + df_petro['Company_name'].astype(str) + ' in ' + df_petro['City / Address'].astype(str) + ', ' + df_petro['Country'].astype(str)
    keywords = df_petro['keyword_search'].to_list()
    return keywords


