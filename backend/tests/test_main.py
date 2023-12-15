import os
import sys
import pytest

# Add the project root to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import requests

from app.mymodules.csv_cleaning import cleancsv1

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

@patch('os.path.exists')
@patch('app.mymodules.csv_cleaning.cleancsv1')
@patch('builtins.print')
def test_merged_data_csv_missing(mock_print, mock_cleancsv1, mock_exists):
    # Adjusted to check for the full path of merged_data.csv
    mock_exists.side_effect = lambda path: False if 'app/merged_data.csv' in path else True

    # Call the endpoint that would trigger the check for merged_data.csv
    response = client.get("/cleaned_csv_show")  # Replace with the appropriate endpoint

    # Ensure the print statement was called with the expected message
    mock_print.assert_called_with("Merged data file not found. Running cleancsv1 to generate it.")

    # Ensure cleancsv1 function was called
    mock_cleancsv1.assert_called_with('app/regpie-RifugiOpenDa_2296-all.csv', 'app/mountain_shelters.csv')
    
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

