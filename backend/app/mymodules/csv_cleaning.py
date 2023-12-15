import pandas as pd
import numpy as np
import os

def cleancsv1(file_path_regpie, file_path_shelters, delimiter=';'):
    file_path_shelters = 'app/mountain_shelters.csv'
    
    # Extract the directory from file_path_shelters
    directory = os.path.dirname(file_path_shelters)

    # Define the output file with the same directory as file_path_shelters
    output_file = os.path.join(directory, 'merged_data.csv')

    # Read and clean the first CSV
    data = pd.read_csv(file_path_regpie, delimiter=delimiter)

    # Convert column names to uppercase
    data.columns = data.columns.str.upper()

    # Dropping columns
    drop_indexes = [0, 1, 4, 5, 8, 9, 40] + list(range(11, 39))
    data.drop(data.columns[drop_indexes], axis=1, inplace=True)
    
    # Dropping all columns after index 43
    data = data.iloc[:, :8]

    # Moving 'Denominazione Struttura' to index 0
    denominazione_col = data.pop('DENOMINAZIONESTRUTTURA')
    data.insert(0, 'DENOMINAZIONE', denominazione_col)
    # Drop any row with 'DENOMINAZIONE' value "camposecco"
    data = data[data['DENOMINAZIONE'].str.lower() != "camposecco"]
    
    # Drop duplicate entries based on 'DENOMINAZIONE'
    data.drop_duplicates(subset='DENOMINAZIONE', keep='first', inplace=True)

    # Rename the last three columns
    new_column_names = {data.columns[5]: 'CAMERE', data.columns[6]: 'LETTI', data.columns[7]: 'BAGNI'}
    data.rename(columns=new_column_names, inplace=True)

    # Fill NaN values in integer columns with 0 and then change the format to integer
    integer_columns = ['CAMERE', 'LETTI', 'BAGNI']
    data[integer_columns] = data[integer_columns].fillna(0).astype(int)

    # Replace NaN values with '---'
    data.fillna('---', inplace=True)

    # Replace phone numbers that don't have at least 10 digits with '---'
    data['TELEFONO'] = data['TELEFONO'].apply(lambda x: '---' if len(str(x)) < 10 else x)

    # Read the second CSV
    shelters = pd.read_csv(file_path_shelters)
    # Convert 'Latitude' and 'Longitude' in shelters DataFrame to float
    shelters['Latitude'] = pd.to_numeric(shelters['Latitude'], errors='coerce')
    shelters['Longitude'] = pd.to_numeric(shelters['Longitude'], errors='coerce')

    # Custom function to find partial, case-insensitive match
    def partial_match(denominazione, df_shelters):
        for index, row in df_shelters.iterrows():
            if denominazione.lower() in row['Name'].lower():
                return row.name
        return None

    # Apply the custom function to find a merge key
    data['merge_key'] = data['DENOMINAZIONE'].apply(lambda x: partial_match(x, shelters))

    # Merge the dataframes
    merged_data = pd.merge(data, shelters, left_on='merge_key', right_index=True, how='left')

    merged_data['Description'] = merged_data['Description'].fillna('No description available')

    # Drop the temporary merge key and 'DENOMINAZIONE' column
    merged_data.drop(['merge_key', 'DENOMINAZIONE'], axis=1, inplace=True)

    # Rename 'Name' from second DataFrame to 'DENOMINAZIONE' in the merged DataFrame
    merged_data.rename(columns={'Name': 'DENOMINAZIONE'}, inplace=True)

    # Filter out rows where coordinates are NaN
    # Replace 'Latitude' and 'Longitude' with your actual coordinate column names
    merged_data = merged_data.dropna(subset=['Latitude', 'Longitude'])
    
    # Save the merged DataFrame to a CSV file in the same directory
    merged_data.to_csv(output_file, index=False)
    # print(f"File '{output_file}' saved successfully.")

    return merged_data

# # Usage
# file_path_regpie = 'app/regpie-RifugiOpenDa_2296-all.csv'  # Update with your file path
# Update with your file path
# merged_data = cleancsv1(file_path_regpie, file_path_shelters)
# print(merged_data)
