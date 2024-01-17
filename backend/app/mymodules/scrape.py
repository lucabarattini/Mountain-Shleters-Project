import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import os


def scrape_shelter_urls(test_mode=False):
    """
    Scrapes shelter URLs from a website. If test_mode is True,
    only the first 20 URLs are scraped.
    """
    cache_file = "backend/app/urls_cache.txt"

    if os.path.exists(cache_file) and not test_mode:
        print("Loading URLs from cache...")
        with open(cache_file, 'r') as file:
            urls = file.read().splitlines()
        return urls

    urls = []
    base_url = "https://www.escursionismo.it/rifugi-bivacchi/"
    response = requests.get(base_url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find total number of pages to scrape
    total_pages = int(soup.find_all('a', class_='page-numbers')
                      [-2].text) if not test_mode else 1

    # Iterate over each page and scrape URLs
    for page in tqdm(range(1, total_pages + 1), desc="Scraping Pages"):
        page_url = f"{base_url}page/{page}/" if page > 1 else base_url
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract shelter URLs from the current page
        for div in soup.find_all('div', class_='profile-name'):
            a_tag = div.find('a')
            if a_tag and 'href' in a_tag.attrs:
                urls.append(a_tag['href'])
                if test_mode and len(urls) >= 20:
                    return urls

    # Save scraped URLs to cache file
    if not test_mode:
        with open(cache_file, 'w') as file:
            for url in urls:
                file.write(f"{url}\n")

    return urls


def scrape_shelter_details(url):
    """
    Scrapes details of a shelter from its URL.

    Attempts to scrape shelter name, description, region, and coordinates from
    the given URL. Handles exceptions and returns a default dictionary with
    error messages in case of failure.

    Parameters:
    url (str): The URL of the shelter to scrape.

    Returns:
    dict: A dictionary containing scraped details of the shelter.
    """
    details = {}

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract shelter name
        name_tag = soup.find('h3', style="margin-top: 25px")
        details['Name'] = name_tag.text.strip(
        ) if name_tag else 'Name not found'

        # Extract shelter description
        description_tag = soup.find('div', class_='descrizione-lunga')
        details['Description'] = description_tag.text.strip(
        ) if description_tag else 'Description not found'

        # Extract region information
        details['Region'] = 'Region not found'
        for td in soup.find_all('td'):
            if td.text.strip() == 'Piemonte':
                details['Region'] = 'Piemonte'
                break

        # Extract coordinates
        details['Latitude'] = 'Coords not found'
        details['Longitude'] = 'Coords not found'
        for td in soup.find_all('td'):
            if 'Lat:' in td.text and 'Long:' in td.text:
                coords = td.get_text(separator="|").split('|')
                if len(coords) >= 2:
                    lat, long = coords[0].split(':'), coords[1].split(':')
                    details['Latitude'] = lat[1].strip()
                    details['Longitude'] = long[1].strip()
                break

    except requests.exceptions.RequestException as e:
        details = {'Name': 'Request failed', 'Description': 'Request failed',
                   'Latitude': 'Request failed', 'Longitude': 'Request failed',
                   'Region': 'Request failed'}
    except Exception as e:
        details = {'Name': 'Error occurred', 'Description': 'Error occurred',
                   'Latitude': 'Error occurred', 'Longitude': 'Error occurred',
                   'Region': 'Error occurred'}

    return details


def process_url(url):
    """
    Processes a single shelter URL to scrape details.

    Calls `scrape_shelter_details` and filters results for 'Piemonte' region.

    Parameters:
    url (str): The URL of the shelter to process.

    Returns:
    dict or None: Shelter details if from 'Piemonte' region, otherwise None.
    """
    details = scrape_shelter_details(url)
    if details['Region'] == 'Piemonte':
        return details
    return None


def main():
    """
    Main function to scrape shelter URLs and details.

    Scrapes all shelter URLs, uses ThreadPoolExecutor to scrape details in
    parallel, and saves details of shelters from 'Piemonte' region to a CSV.
    """
    all_shelter_urls = scrape_shelter_urls()

    all_shelter_details = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submitting URLs for parallel processing
        future_to_url = {executor.submit(
            process_url, url): url for url in all_shelter_urls}

        # Collecting results with progress tracking
        for future in tqdm(as_completed(future_to_url),
                           total=len(all_shelter_urls),
                           desc="Scraping Shelter Details"):
            result = future.result()
            if result:
                all_shelter_details.append(result)

    # Saving shelter details to CSV
    csv_file = 'backend/app/mountain_shelters.csv'
    df = pd.DataFrame(all_shelter_details)
    df.to_csv(csv_file, index=False)
    print(f"CSV file created at {csv_file} with shelter details.")


if __name__ == "__main__":
    main()
