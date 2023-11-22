"""
Backend module for the FastAPI application.

This module defines a FastAPI application that serves
as the backend for the project.
"""

from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime

from .mymodules.birthdays import return_birthday, print_birthdays_str

app = FastAPI()

# Dictionary of birthdays
birthdays_dictionary = {
    'Albert Einstein': '03/14/1879',
    'Benjamin Franklin': '01/17/1706',
    'Ada Lovelace': '12/10/1815',
    'Donald Trump': '06/14/1946',
    'Rowan Atkinson': '01/6/1955'
}


@app.get('/')
def read_root():
    """
    Root endpoint for the backend.

    Returns:
        dict: A simple greeting.
    """
    return {"Hello": "World"}


@app.get('/query/{person_name}')
def read_item(person_name: str):
    """
    Endpoint to query birthdays based on person_name.

    Args:
        person_name (str): The name of the person.

    Returns:
        dict: Birthday information for the provided person_name.
    """
    person_name = person_name.title()  # Convert to title case for consistency
    birthday = birthdays_dictionary.get(person_name)
    if birthday:
        return {"person_name": person_name, "birthday": birthday}
    else:
        return {"error": "Person not found"}


@app.get('/module/search/{person_name}')
def read_item_from_module(person_name: str):
    return {return_birthday(person_name)}


@app.get('/module/all')
def dump_all_birthdays():
    return {print_birthdays_str()}


@app.get('/get-date')
def get_date():
    """
    Endpoint to get the current date.

    Returns:
        dict: Current date in ISO format.
    """
    current_date = datetime.now().isoformat()
    return JSONResponse(content={"date": current_date})
