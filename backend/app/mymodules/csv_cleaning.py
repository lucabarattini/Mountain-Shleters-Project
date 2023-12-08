import pandas as pd
import numpy as np

def cleancsv1(file_path, delimiter=';'):
    data = pd.read_csv(file_path, delimiter=delimiter)

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
    data['TELEFONO'] = data['TELEFONO'].apply(lambda x: x if pd.isna(x) or len(str(x)) >= 10 else '---')

    print(data)
    return data