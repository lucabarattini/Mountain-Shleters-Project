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

from .mymodules.birthdays import return_birthday, print_birthdays_str
from .mymodules.csv_cleaning import cleancsv1

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

    # Return the cleaned data
    return cleaned_data

cleaned_df = cleancsv1('app/regpie-RifugiOpenDa_2296-all.csv')
print(cleaned_df)

# # Call the function and store the result in a variable
# processed_df = process_data(file_path)

# # Display the modified DataFrame
# print(processed_df)
