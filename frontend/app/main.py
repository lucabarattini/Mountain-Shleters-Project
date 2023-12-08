"""
Frontend module for the Flask application.

This module defines a simple Flask application that serves as the frontend for the project.
"""

from flask import Flask, render_template, request
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure secret key

# Configuration for the FastAPI backend URL
FASTAPI_BACKEND_HOST = 'http://backend'  # Replace with the actual URL of your FastAPI backend
BACKEND_URL = f'{FASTAPI_BACKEND_HOST}/query/'

class QueryForm(FlaskForm):
    person_name = StringField('Person Name:')
    submit = SubmitField('Get Birthday from FastAPI Backend')

@app.context_processor
def context_processor():
    return dict(fetch_shelter_info=fetch_shelter_info)

def fetch_shelter_info(shelter_name):
    """
    Fetch complete shelter info, including trail info and coordinates, from the backend.

    Args:
        shelter_name (str): Name of the shelter.

    Returns:
        dict: Data from the backend.
    """
    backend_url = f'http://backend:80/check_shelter/{shelter_name}'
    try:
        response = requests.get(backend_url)
        response.raise_for_status()
        result = response.json()
        # Ensure 'data' key is always present
        if 'data' not in result:
            result['data'] = {}
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error fetching information from backend: {e}")
        return {'found': False, 'data': {}}

@app.route('/')
def index():
    """
    Render the index page.

    Returns:
        str: Rendered HTML content for the index page.
    """
    return render_template('index.html')

@app.route('/piemonte')
def piemonte():
    # Fetch query parameters
    bagni = request.args.get('bagni')
    camere = request.args.get('camere')
    letti = request.args.get('letti')
    provincia = request.args.get('provincia')
    comune = request.args.get('comune')

    # Fetch data from the backend
    response = requests.get('http://backend:80/cleaned_csv_show')
    response.raise_for_status()
    cleaned_data = response.json()

    # Apply filters
    if bagni or camere or letti or provincia or comune:
        filtered_data = []
        for item in cleaned_data:
            # Check each filter criteria
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

            # If the item passes all filters, add it to filtered_data
            filtered_data.append(item)

        cleaned_data = filtered_data
    return render_template('piemonte.html', cleaned_data=cleaned_data)

@app.route('/lombardia')
def lombardia():
    """
    Render the Lombardia page.

    Returns:
        str: Rendered HTML content for the Lombardia page.
    """
    return render_template('lombardia.html')

@app.route('/friuli')
def friuli():
    """
    Render the Friuli page.

    Returns:
        str: Rendered HTML content for the Friuli page.
    """
    return render_template('friuli.html')

@app.route('/project_description')
def project_description():
    return render_template('project_description.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)