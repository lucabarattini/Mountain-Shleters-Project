import pandas as pd
import numpy as np
import os

def clean_csv1(file_path_regpie, file_path_shelters, delimiter=';'):
    """
    Merge and clean data from two CSV files containing information about 
    mountain shelters.

    Parameters:
    file_path_regpie (str): File path for the first CSV file to be cleaned.
    file_path_shelters (str): File path for the second CSV file containing 
                              shelter data.
    delimiter (str, optional): Delimiter used in the CSV files. Defaults to ';'.

    Returns:
    pd.DataFrame: A pandas DataFrame containing merged and cleaned data from
                  both input CSV files.
    """
    file_path_shelters = 'app/mountain_shelters.csv'

    # Get the directory of the shelters file
    directory = os.path.dirname(file_path_shelters)

    # Construct the output file path in the same directory
    output_file = os.path.join(directory, 'merged_data.csv')

    # Read the first CSV file
    data = pd.read_csv(file_path_regpie, delimiter=delimiter)

    # Convert all column names in the first CSV to uppercase
    data.columns = data.columns.str.upper()

    # Define indexes of columns to drop and then drop them
    drop_indexes = [0, 1, 4, 5, 8, 9, 40] + list(range(11, 39))
    data.drop(data.columns[drop_indexes], axis=1, inplace=True)

    # Keep only the first 8 columns of the data
    data = data.iloc[:, :8]

    # Move 'DENOMINAZIONESTRUTTURA' column to the first position
    denom_col = data.pop('DENOMINAZIONESTRUTTURA')
    data.insert(0, 'DENOMINAZIONE', denom_col)

    # Remove rows where 'DENOMINAZIONE' is 'camposecco'
    data = data[data['DENOMINAZIONE'].str.lower() != "camposecco"]

    # Remove duplicate rows based on 'DENOMINAZIONE'
    data.drop_duplicates(subset='DENOMINAZIONE', keep='first', inplace=True)

    # Rename specific columns for clarity
    new_col_names = {
        data.columns[5]: 'CAMERE', 
        data.columns[6]: 'LETTI', 
        data.columns[7]: 'BAGNI'
    }
    data.rename(columns=new_col_names, inplace=True)

    # Fill NaNs in 'CAMERE', 'LETTI', and 'BAGNI' with 0 and convert to int
    int_cols = ['CAMERE', 'LETTI', 'BAGNI']
    data[int_cols] = data[int_cols].fillna(0).astype(int)

    # Replace other NaNs with '---' and fix phone number format
    data.fillna('---', inplace=True)
    data['TELEFONO'] = data['TELEFONO'].apply(
        lambda x: '---' if len(str(x)) < 10 else x)

    # Read the second CSV file
    shelters = pd.read_csv(file_path_shelters)

    # Convert 'Latitude' and 'Longitude' in the shelters DataFrame to floats
    shelters['Latitude'] = pd.to_numeric(shelters['Latitude'], errors='coerce')
    shelters['Longitude'] = pd.to_numeric(shelters['Longitude'], errors='coerce')

    # Nested function to find a partial, case-insensitive match
    def partial_match(denominazione, df_shelters):
        """
        Find partial, case-insensitive match for a name in shelters DataFrame.
        """
        for _, row in df_shelters.iterrows():
            if denominazione.lower() in row['Name'].lower():
                return row.name
        return None

    # Apply the partial_match function to create a merge key
    data['merge_key'] = data['DENOMINAZIONE'].apply(
        lambda x: partial_match(x, shelters))

    # Merge the two dataframes based on the merge key
    merged_data = pd.merge(data, shelters, left_on='merge_key', 
                           right_index=True, how='left')

    # Fill missing descriptions with a default text
    merged_data['Description'] = merged_data['Description'].fillna(
        'No description available')

    # Drop the temporary merge key and 'DENOMINAZIONE' column
    merged_data.drop(['merge_key', 'DENOMINAZIONE'], axis=1, inplace=True)

    # Rename 'Name' from the shelters DataFrame to 'DENOMINAZIONE'
    merged_data.rename(columns={'Name': 'DENOMINAZIONE'}, inplace=True)

    # Drop rows where coordinates are NaN
    merged_data = merged_data.dropna(subset=['Latitude', 'Longitude'])

    # Save the merged DataFrame to a CSV
    merged_data.to_csv(output_file, index=False)
    # print(f"File '{output_file}' saved successfully.")

    return merged_data