import os
import sys
import pytest
import pandas as pd
import numpy as np

from concurrent.futures import ThreadPoolExecutor, Future

# Add the project root to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, mock_open, call
import requests

from app.mymodules.csv_cleaning import clean_csv1
from app.mymodules.scrape import main, process_url, scrape_shelter_details, scrape_shelter_urls

"""
Execute this test by running on the terminal (from the app/) the command:
pytest --cov=app --cov-report=html tests/
 """
 
# Add the project root to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

client = TestClient(app)

@patch('requests.get')
def test_get_coordinates_exception(mock_get):
    invalid_location = "InvalidLocation"
    range_km = "5"
    mock_get.side_effect = requests.exceptions.RequestException("An error occurred")
    response = client.get(f"/cleaned_csv_show?location={invalid_location}&range_km={range_km}")
    assert response.status_code == 200  # or another appropriate status code
    assert response.json() == {"error": "💀 Invalid location. Please re-enter a valid location."}

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Your Backend is running :)"}

def test_valid_province_filter():
    province_name = "VERBANO-CUSIO-OSSOLA"  # Replace with a valid province name from your dataset
    response = client.get(f"/cleaned_csv_show?provincia={province_name}")
    assert response.status_code == 200
    assert all(item['PROVINCIA'] == province_name for item in response.json())

def test_invalid_province_filter():
    response = client.get("/cleaned_csv_show?provincia=InvalidProvince")
    assert response.status_code == 200
    assert response.json() == {"error": "No results found for the PROVINCIA 'InvalidProvince'"}

def test_valid_comune_filter():
    comune_name = "ENTRACQUE"  # Replace with a valid comune name from your dataset
    response = client.get(f"/cleaned_csv_show?comune={comune_name}")
    assert response.status_code == 200
    assert all(item['COMUNE'] == comune_name for item in response.json())

def test_invalid_comune_filter():
    response = client.get("/cleaned_csv_show?comune=InvalidComune")
    assert response.status_code == 200
    assert response.json() == {"error": "No results found for the COMUNE 'InvalidComune'"}

def test_valid_bagni_filter():
    valid_bagni = "40"  # This is a string
    response = client.get(f"/cleaned_csv_show?bagni={valid_bagni}")
    assert response.status_code == 200
    assert all(item['BAGNI'] == int(valid_bagni) for item in response.json())

def test_invalid_bagni_filter():
    invalid_bagni = "-1"  # Example of an invalid number of bathrooms
    response = client.get(f"/cleaned_csv_show?bagni={invalid_bagni}")
    assert response.status_code == 200
    # Adjust this to match the actual API response for invalid input
    assert response.json() == []  # or a different error structure

def test_valid_camere_filter():
    valid_camere = "1"  # Replace with a valid number of rooms
    response = client.get(f"/cleaned_csv_show?camere={valid_camere}")
    assert response.status_code == 200
    assert all(item['CAMERE'] == int(valid_camere) for item in response.json())

def test_invalid_camere_filter():
    invalid_camere = "-1"  # Example of an invalid number of rooms
    response = client.get(f"/cleaned_csv_show?camere={invalid_camere}")
    assert response.status_code == 200
    # Adjust this to match the actual API response for invalid input
    assert response.json() == []  # or a different error structure

def test_valid_letti_filter():
    valid_letti = "1"  # Replace with a valid number of beds
    response = client.get(f"/cleaned_csv_show?letti={valid_letti}")
    assert response.status_code == 200
    assert all(item['LETTI'] == int(valid_letti) for item in response.json())

def test_invalid_letti_filter():
    invalid_letti = "-1"  # Example of an invalid number of beds
    response = client.get(f"/cleaned_csv_show?letti={invalid_letti}")
    assert response.status_code == 200
    # Adjust this to match the actual API response for invalid input
    assert response.json() == []  # or a different error structure

def test_location_and_range_filter():
    valid_location = "BACENO VB"  # Replace with a valid location
    range_km = "20.0"  # Replace with a valid range in KM
    response = client.get(f"/cleaned_csv_show?location={valid_location}&range_km={range_km}")
    assert response.status_code == 200
    assert 'Distance' in response.json()[0]  # Check if distance key exists

def test_invalid_location_and_range_filter():
    invalid_location = "InvalidLocation"
    range_km = "-10.0"  # Example of an invalid range
    response = client.get(f"/cleaned_csv_show?location={invalid_location}&range_km={range_km}")
    assert response.status_code == 200
    # Update the expected error message to match the actual API response
    assert response.json() == {"error": "💀 Invalid location. Please re-enter a valid location."}


def test_no_filter():
    response = client.get("/cleaned_csv_show")
    assert response.status_code == 200
    assert type(response.json()) is list
    
@patch('os.path.exists')
@patch('builtins.open', new_callable=mock_open, read_data='url1\nurl2\n')
def test_scrape_shelter_urls_cache_loading(mock_open, mock_exists):
    mock_exists.return_value = True
    urls = scrape_shelter_urls()
    mock_open.assert_called_once_with('backend/app/urls_cache.txt', 'r')
    assert urls == ['url1', 'url2']
    
# @patch('app.mymodules.scrape.os.path.exists')
# @patch('app.mymodules.scrape.open', new_callable=mock_open)
# def test_scrape_shelter_urls_cache_loading(mock_file_open, mock_exists):
#     # Simulate that the cache file does not exist
#     mock_exists.return_value = False

#     # Call the function, which should perform scraping and save results to cache
#     urls = scrape_shelter_urls(test_mode=True)

#     # Assert that the function scraped at least the first two links
#     assert len(urls) >= 2, "At least 2 URLs should be scraped"

#     # Verify that the function attempted to save the scraped URLs to the cache file
#     mock_file_open.assert_called_once_with('backend/app/urls_cache.txt', 'w')
#     handle = mock_file_open()
#     assert handle.write.call_count == len(urls), "Each URL should be written to the cache file"
    
def test_clean_csv1_with_actual_data():
    # Define the actual file paths for your CSV files
    file_path_regpie = 'app/regpie-RifugiOpenDa_2296-all.csv'
    file_path_shelters = 'app/mountain_shelters.csv'

    # Call the function with actual data
    result = clean_csv1(file_path_regpie, file_path_shelters)

    # Assertions
    # Replace these with assertions relevant to your function's expected behavior
    assert isinstance(result, pd.DataFrame)
    assert 'CAMERE' in result.columns
    assert 'LETTI' in result.columns
    assert 'BAGNI' in result.columns
    
    
def test_scrape_shelter_urls_real_page():
    # Call the function in test mode
    urls = scrape_shelter_urls(test_mode=True)

    # Assertions
    assert len(urls) >= 2
    print(urls)
    # Check if the specific URL is in the scraped list
    expected_url = "https://www.escursionismo.it/rifugi-bivacchi/a-neuve-cabane-de-l'-15043"
    assert expected_url in urls, f"The expected URL {expected_url} was not found in the scraped URLs."
    
def test_scrape_shelter_details_real_urls():
    # Define the URLs to test
    urls = [
        'https://www.escursionismo.it/rifugi-bivacchi/3a-14998',
    ]

    # Expected details 
    expected_details = {
        'Name': 'Rifugio non custodito - ADM - Alpe Pozzolo [1640m]',
        'Description': """Dal municipio di Beura si segue la stradina che entra in paese e passa sotto un arco; 
        si imbocca la bella mulattiera di fronte (cartello indicatore per l’Alpe Pozzolo e segnavia bianco-rosso)
        che guadagna quota rapidamente. Oltre una cappelletta e si raggiungono due baite diroccate; subito dopo si 
        lascia a destra (cartelli indicatori) la mulattiera per l’alpe Bisoggio e si sale fino all’Alpe Cresta 
        (o Alpe Caggiani, 460 m). Si costeggia a destra il prato dell’alpeggio, si supera la balza rocciosa a 
        monte delle case (scalinata) e, dopo alcuni tornanti, con un lungo diagonale verso NE si giunge all’Alpe
        Fiesco 600 m. Il sentiero volge ora a destra e risale un ripido costone entrando nella faggeta; piegando 
        ancora verso destra (S) si arriva all’Alpe Vaccareccia. Dalla fontanella (880 m circa) si entra nel bosco 
        sorvegliato all’inizio da alcuni castagni monumentali. Dopo alcuni tornanti si va a destra e oltre uno 
        speroncino roccioso si lambiscono due baite; proseguendo nel bosco si sale alla radura di Pra o Menga 
        (baita, cappelletta e fontanella). Il costone diviene molto meno ripido: dopo un tratto sul suo fianco 
        sinistro (N), il sentiero raggiunge il crinale e con alcuni saliscendi si arriva all’Alpe Provo 1205 m, 
        con una caratteristica fontana di sasso. Poco oltre il crinale torna ripido: a quota 1280 circa il 
        sentiero segnalato taglia sul ripido fianco sinistro (N) del costone giungendo sul fondo del vallone 
        dove scorre il torrente e dove si incontra un bivio segnalato: a sinistra si va all’alpe Cortevecchio,
        a destra si sale verso il rifugio Alpe Bozzolo. Più in alto, presso un altro torrentello, un nuovo
        piccolo cartello manda decisamente a destra riportando sul filo del crestone verso i 1520 m e lo 
        si segue fino al bellissimo dosso dove sorge il rifugio.""",
        'Region': 'Piemonte'
    }


    for url in urls:
        # Call the function
        details = scrape_shelter_details(url)

        # Assertions
        assert details['Name'] != 'Name not found', "Name should be found"
        assert details['Description'] != 'Description not found', "Description should be found"
        assert details['Region'] != 'Region not found', "Region should be found"

def test_process_url():
    # URL for a shelter in the 'Piemonte' region
    piemonte_url = "https://www.escursionismo.it/rifugi-bivacchi/3a-14998"
    
    # URL for a shelter outside the 'Piemonte' region
    non_piemonte_url = "https://www.escursionismo.it/rifugi-bivacchi/a-neuve-cabane-de-l'-15043"

    # Process the Piemonte URL
    piemonte_details = process_url(piemonte_url)
    assert piemonte_details is not None, "Piemonte shelter should return details"
    assert piemonte_details['Region'] == 'Piemonte', "Region should be Piemonte"

    # Process the non-Piemonte URL
    non_piemonte_details = process_url(non_piemonte_url)
    assert non_piemonte_details is None, "Non-Piemonte shelter should return None"



# def mock_process_url(url):
#     if "piemonte" in url:
#         return {"URL": url, "Region": "Piemonte"}
#     return None

# def create_future(result):
#     future = Future()
#     future.set_result(result)
#     return future

# @patch('app.mymodules.scrape.scrape_shelter_urls')
# @patch('app.mymodules.scrape.ThreadPoolExecutor')
# @patch('builtins.open', new_callable=MagicMock)
# def test_main(mock_open, mock_executor, mock_scrape_shelter_urls):
#     mock_shelter_urls = ['https://www.escursionismo.it/rifugi-bivacchi/piemonte-rifugio1', 
#                          'https://www.escursionismo.it/rifugi-bivacchi/other-region-rifugio2']
#     mock_scrape_shelter_urls.return_value = mock_shelter_urls

#     # Mock the ThreadPoolExecutor submit method
#     mock_executor.return_value.__enter__.return_value.submit.side_effect = lambda func, url: create_future(func(url))

#     # Call the main function
#     main()

#     # Check if scrape_shelter_urls was called
#     mock_scrape_shelter_urls.assert_called_once()

#     # Check if ThreadPoolExecutor was used
#     assert mock_executor.return_value.__enter__.return_value.submit.call_count == len(mock_shelter_urls)

#     # Check if the CSV file was created
#     mock_open.assert_called_once_with('backend/app/mountain_shelters.csv', 'w')

#     # Optionally, verify the content written to the file
#     # ...

#     # Clean up - remove the created CSV file
#     if os.path.exists('backend/app/mountain_shelters.csv'):
#         os.remove('backend/app/mountain_shelters.csv')