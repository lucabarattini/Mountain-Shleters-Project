"""
Backend module for the FastAPI application.

This module defines a FastAPI application that serves
as the backend for the project.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import pandas as pd
from haversine import haversine

from .mymodules.csv_cleaning import cleancsv1
from .mymodules.csv_cleaning_2 import cleancsv2
from .mymodules.csv_cleaning_3 import cleancsv3
import json
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Your Backend is running :)"}

@app.on_event("startup")
async def startup_event():
    print("Your Backend is running: 🌈")

# Google API key
GOOGLE_API_KEY = "AIzaSyATC1fSYrOd7mQufuvHCOZX2CdXptZNvas"  # Replace with your actual API key

def get_coordinates(address):
    """
    Convert an address to geographic coordinates using Google's Geocoding API.
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # This will raise an error for non-200 responses
        data = response.json()
        if data['status'] != 'OK':
            print(f"Error in Geocoding API response: {data['status']}")
            return None, None
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Geocoding API: {e}")
        return None, None

@app.get('/cleaned_csv_show')
async def read_and_return_cleaned_csv(
    bagni: str = Query(None), 
    camere: str = Query(None), 
    letti: str = Query(None), 
    provincia: str = Query(None), 
    comune: str = Query(None), 
    location: str = Query(None), 
    range_km: float = Query(None)
):
    # CSV file paths
    regpie_csv_path = 'app/regpie-RifugiOpenDa_2296-all.csv'
    shelters_csv_path = 'app/mountain_shelters.csv'

    # Process and merge the CSV files
    cleaned_df = cleancsv1(regpie_csv_path, shelters_csv_path)

    # Initialize user coordinates
    user_lat, user_lng = None, None
    if location:
        user_lat, user_lng = get_coordinates(location)
        if user_lat is None or user_lng is None:
            print("Invalid location or unable to get coordinates.")
            raise HTTPException(status_code=400, detail="Invalid location")
        else:
            print(f"User coordinates: Latitude = {user_lat}, Longitude = {user_lng}")

    # Convert the DataFrame to a dictionary for processing
    cleaned_data = cleaned_df.to_dict(orient='records')

    # Apply filters
    filtered_data = []
    for item in cleaned_data:
        if bagni and str(item.get('BAGNI', '')) != bagni:
            continue
        if camere and str(item.get('CAMERE', '')) != camere:
            continue
        if letti and str(item.get('LETTI', '')) != letti:
            continue
        if provincia and item.get('PROVINCIA', '').lower() != provincia.lower():
            continue
        if comune and item.get('COMUNE', '').lower() != comune.lower():
            continue

        # Location-based filtering
        if user_lat is not None and user_lng is not None and 'Latitude' in item and 'Longitude' in item:
            item_lat, item_lng = item['Latitude'], item['Longitude']
            distance = haversine((user_lat, user_lng), (item_lat, item_lng))
            print(f"Distance from {item['DENOMINAZIONE']} to user location: {distance} km")
            if distance > range_km:
                continue

        filtered_data.append(item)

    return JSONResponse(content=filtered_data)


@app.get('/cleaned_csv_2_show')
async def read_and_return_cleaned_csv():
    csv_file_path = 'app/Rifugi_Alpini_Escursionistici.csv'

    # Process the CSV file using the cleancsv2 function
    cleaned_df_2 = cleancsv2(csv_file_path)

    # Convert the processed DataFrame to a dictionary
    cleaned_data_2 = cleaned_df_2.to_dict(orient='records')

    # Return the cleaned data
    return cleaned_data_2

@app.get('/cleaned_csv_3_show')
async def read_and_return_cleaned_csv():
    csv_file_path = 'app/Strutture_Ricettive_Alberghiere_e_extra-alberghiere.csv'

    # Process the CSV file using the cleancsv2 function
    cleaned_df_3 = cleancsv3(csv_file_path)

    # Convert the processed DataFrame to a dictionary
    cleaned_data_3 = cleaned_df_3.to_dict(orient='records')

    # Return the cleaned data
    return cleaned_data_3