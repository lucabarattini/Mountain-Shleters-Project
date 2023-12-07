"""
Backend module for the FastAPI application.

This module defines a FastAPI application that serves
as the backend for the project.
"""

from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import pandas as pd

from .mymodules.csv_cleaning import cleancsv1
from .mymodules.csv_cleaning_2 import cleancsv2
from .mymodules.csv_cleaning_3 import cleancsv3

app = FastAPI()

@app.get('/')
def read_root():
    """
    Root endpoint for the backend.

    Returns:
        dict: A simple greeting confirming it's working.
    """
    return {"Test endpoint API": "It's working"}

@app.get('/cleaned_csv_show')
async def read_and_return_cleaned_csv():
    csv_file_path = 'app/regpie-RifugiOpenDa_2296-all.csv'

    # Process the CSV file using the cleancsv1 function
    cleaned_df = cleancsv1(csv_file_path)

    # Convert the processed DataFrame to a dictionary
    cleaned_data = cleaned_df.to_dict(orient='records')

    # Log the first few records to verify the structure
    print(cleaned_data[:5])  # Print the first 5 records

    # Return the cleaned data
    return cleaned_data

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

@app.get('/check_shelter/{shelter_name}')
async def check_shelter(shelter_name: str):
    """
    Check if a shelter is present in the mountain_shelters.csv file.

    Args:
        shelter_name (str): Name of the shelter to check.

    Returns:
        dict: Contains a boolean indicating if the shelter is found and additional data if available.
    """
    csv_file_path = 'app/mountain_shelters.csv'
    df = pd.read_csv(csv_file_path)

    # Check if the shelter name is in the DataFrame
    shelter_data = df[df['Name'].str.contains(shelter_name, case=False, na=False)]
    if not shelter_data.empty:
        # Extracting first matching record
        record = shelter_data.to_dict(orient='records')[0]
        return {'found': True, 'data': record}
    else:
        return {'found': False}