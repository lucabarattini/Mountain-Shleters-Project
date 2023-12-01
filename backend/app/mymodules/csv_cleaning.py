import pandas as pd

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
    # Ensure the column name is in uppercase as the names have been converted
    denominazione_col = data.pop('DENOMINAZIONESTRUTTURA')
    data.insert(0, 'DENOMINAZIONE', denominazione_col)

    # Replace NaN values with '---'
    data.fillna('---', inplace=True)

    # Rename the last three columns
    new_column_names = {data.columns[5]: 'CAMERE', data.columns[6]: 'LETTI', data.columns[7]: 'BAGNI'}
    data.rename(columns=new_column_names, inplace=True)

    return data