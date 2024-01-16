"""
Frontend module for the Flask application.

This module defines a simple Flask application that serves as the frontend for the project.
"""

from flask import Flask, render_template, request
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  

# Configuration for the FastAPI backend URL
FASTAPI_BACKEND_HOST = 'http://backend'  
BACKEND_URL = f'{FASTAPI_BACKEND_HOST}/query/'

class QueryForm(FlaskForm):
    """Form for submitting queries to the backend."""

    person_name = StringField('Person Name:')
    submit = SubmitField('Get Birthday from FastAPI Backend')

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
    """
    Render the Piemonte page with dynamic content based on query parameters.

    This function fetches data from the backend based on query parameters 
    provided by the user and renders the Piemonte page with this data.

    Returns:
        Rendered HTML content for the Piemonte page.
    """
    # Fetch query parameters
    query_params = {
        'bagni': request.args.get('bagni'),
        'camere': request.args.get('camere'),
        'letti': request.args.get('letti'),
        'provincia': request.args.get('provincia'),
        'comune': request.args.get('comune'),
        'location': request.args.get('location'),
        'range_km': request.args.get('range_km')
    }

    # Fetch data from the backend with query parameters
    response = requests.get('http://backend:80/cleaned_csv_show', params=query_params)
    response.raise_for_status()
    cleaned_data = response.json()
    
    # Check for an error in the response
    if 'error' in cleaned_data:
        error_message = cleaned_data['error']
        # Render the Piemonte page with an error message
        return render_template('piemonte.html', error_message=error_message, cleaned_data=[])

    return render_template('piemonte.html', cleaned_data=cleaned_data)

@app.route('/project_description')
def project_description():
    """
    This function handles the rendering of the project description page.
    """
    return render_template('project_description.html')


if __name__ == '__main__':
    print("🌈 Running on http://localhost:8080")
    app.run(host='0.0.0.0', port=80, debug=False)