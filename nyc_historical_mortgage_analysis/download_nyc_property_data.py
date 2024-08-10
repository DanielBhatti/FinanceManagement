# doesn't seem to be working
# sales data obtained here from 2003 onwards https://www.nyc.gov/site/finance/property/property-annualized-sales-update.page

import requests
from bs4 import BeautifulSoup
import os

def download_excel_files(url, target_folder):
    try:
        # Create target folder if it doesn't exist
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request failed

        # Parse the content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all hyperlinks on the page
        links = soup.find_all('a')

        # Filter links that end with '.xls' or '.xlsx' (Excel files)
        excel_links = [link for link in links if link.get('href') and link.get('href').endswith(('.xls', '.xlsx'))]

        for link in excel_links:
            file_url = link.get('href')
            if not file_url.startswith('http'):
                file_url = url + file_url  # Handle relative URLs

            file_response = requests.get(file_url)
            file_name = file_url.split('/')[-1]
            file_path = os.path.join(target_folder, file_name)

            # Write the file to the target folder
            with open(file_path, 'wb') as file:
                file.write(file_response.content)

            print(f'Downloaded: {file_name}')

    except Exception as e:
        print(f'An error occurred: {e}')

# Example usage
url = 'https://www.nyc.gov/site/finance/property/property-annualized-sales-update.page'
download_excel_files(url, 'downloaded_excel_files')
