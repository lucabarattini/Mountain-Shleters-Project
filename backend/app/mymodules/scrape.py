import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

def scrape_shelter_urls():
    """
    Scrapes all shelter URLs from 'https://www.escursionismo.it/rifugi-bivacchi/'.
    Utilizes caching to store and retrieve the URLs, reducing the need for repeated scraping.
    The cache is stored in 'backend/app/urls_cache.txt'.
    """
    cache_file = "backend/app/urls_cache.txt"

    if os.path.exists(cache_file):
        print("Loading URLs from cache...")
        with open(cache_file, 'r') as file:
            urls = file.read().splitlines()
        return urls

    urls = []
    base_url = "https://www.escursionismo.it/rifugi-bivacchi/"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    total_pages = int(soup.find_all('a', class_='page-numbers')[-2].text)

    for page in tqdm(range(1, total_pages + 1), desc="Scraping Pages"):
        page_url = f"{base_url}page/{page}/" if page > 1 else base_url
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        for div in soup.find_all('div', class_='profile-name'):
            a_tag = div.find('a')
            if a_tag and 'href' in a_tag.attrs:
                urls.append(a_tag['href'])

    with open(cache_file, 'w') as file:
        for url in urls:
            file.write("%s\n" % url)

    return urls

def scrape_shelter_details(url):
    details = {}

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        name_tag = soup.find('h3', style="margin-top: 25px")
        details['Name'] = name_tag.text.strip() if name_tag else 'Name not found'

        description_tag = soup.find('div', class_='descrizione-lunga')
        details['Description'] = description_tag.text.strip() if description_tag else 'Description not found'

        # Extracting region information
        details['Region'] = 'Region not found'
        for td in soup.find_all('td'):
            if td.text.strip() == 'Piemonte':
                details['Region'] = 'Piemonte'
                break

        # Extracting coordinates
        details['Latitude'], details['Longitude'] = 'Coordinates not found', 'Coordinates not found'
        for td in soup.find_all('td'):
            if 'Lat:' in td.text and 'Long:' in td.text:
                coords = td.get_text(separator="|").split('|')
                if len(coords) >= 2:
                    details['Latitude'] = coords[0].split(':')[1].strip()
                    details['Longitude'] = coords[1].split(':')[1].strip()
                break

    except requests.exceptions.RequestException as e:
        details = {'Name': 'Request failed', 'Description': 'Request failed', 'Latitude': 'Request failed', 'Longitude': 'Request failed', 'Region': 'Request failed'}
    except Exception as e:
        details = {'Name': 'Error occurred', 'Description': 'Error occurred', 'Latitude': 'Error occurred', 'Longitude': 'Error occurred', 'Region': 'Error occurred'}

    return details

def process_url(url):
    # This function will process each URL
    details = scrape_shelter_details(url)
    if details['Region'] == 'Piemonte':
        return details
    return None

def main():
    all_shelter_urls = scrape_shelter_urls()

    # Using ThreadPoolExecutor to scrape in parallel
    all_shelter_details = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all the URLs to the executor
        future_to_url = {executor.submit(process_url, url): url for url in all_shelter_urls}

        # Use tqdm for progress tracking
        for future in tqdm(as_completed(future_to_url), total=len(all_shelter_urls), desc="Scraping Shelter Details"):
            result = future.result()
            if result:
                all_shelter_details.append(result)

    # Save to CSV
    csv_file = 'backend/app/mountain_shelters.csv'
    df = pd.DataFrame(all_shelter_details)
    df.to_csv(csv_file, index=False)
    print(f"CSV file created at {csv_file} with shelter details.")

if __name__ == "__main__":
    main()