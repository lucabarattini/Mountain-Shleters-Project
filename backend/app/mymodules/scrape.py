import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import os

def scrape_shelter_urls():
    """
    Scrapes the first 20 shelter URLs from 'https://www.escursionismo.it/rifugi-bivacchi/'.
    Utilizes caching to store and retrieve the URLs, reducing the need for repeated scraping.
    The cache is stored in 'backend/app/urls_cache.txt'.
    """
    cache_file = "backend/app/urls_cache.txt"

    # Check if the cache file exists and read from it
    if os.path.exists(cache_file):
        print("Loading URLs from cache...")
        with open(cache_file, 'r') as file:
            urls = file.read().splitlines()
        return urls[:20]

    urls = []
    base_url = "https://www.escursionismo.it/rifugi-bivacchi/"

    # Counter for the number of URLs
    url_count = 0

    # Initial request to get the total number of pages
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    total_pages = int(soup.find_all('a', class_='page-numbers')[-2].text)

    for page in tqdm(range(1, total_pages + 1), desc="Scraping Pages"):
        if url_count >= 20:
            break

        page_url = f"{base_url}page/{page}/" if page > 1 else base_url
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        for div in soup.find_all('div', class_='profile-name'):
            a_tag = div.find('a')
            if a_tag and 'href' in a_tag.attrs:
                urls.append(a_tag['href'])
                url_count += 1

                if url_count >= 20:
                    break

    # Save the URLs to cache file
    with open(cache_file, 'w') as file:
        for url in urls:
            file.write("%s\n" % url)

    return urls

def scrape_shelter_details(url):
    """
    Scrapes detailed information for a single shelter from the provided URL.
    Extracts the shelter's name and description and returns them in a dictionary.
    """
    details = {}

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        name_tag = soup.find('h3', style="margin-top: 25px")
        if name_tag:
            details['Name'] = name_tag.text.strip()
        else:
            details['Name'] = 'Name not found'

        description_tag = soup.find('div', class_='descrizione-lunga')
        if description_tag:
            details['Description'] = description_tag.text.strip()
        else:
            details['Description'] = 'Description not found'

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        details['Name'] = 'Request failed'
        details['Description'] = 'Request failed'
    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")
        details['Name'] = 'Error occurred'
        details['Description'] = 'Error occurred'

    return details

def main():
    """
    Main function that orchestrates the scraping of shelter URLs and their details.
    Stores the results in a CSV file located at 'backend/app/mountain_shelters.csv'.
    """
    all_shelter_urls = scrape_shelter_urls()
    all_shelter_details = []

    for url in tqdm(all_shelter_urls, desc="Scraping Shelter Details"):
        details = scrape_shelter_details(url)
        all_shelter_details.append(details)

    # Create DataFrame and save to CSV
    csv_file = 'backend/app/mountain_shelters.csv'
    df = pd.DataFrame(all_shelter_details)
    df.to_csv(csv_file, index=False)
    print(f"CSV file created at {csv_file} with shelter details.")

if __name__ == "__main__":
    main()