import pandas as pd

def cleancsv3(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Define the criteria for filtering
    condition_column = 'CLASSIFICAZIONE'
    condition_value = 'Rifugi di montagna'

    # Use boolean indexing to filter the dataframe
    df = df[df[condition_column] == condition_value]

    # Define the columns to keep
    columns_to_keep = [1, 2, 3, 6, 11, 12, 15, 17, 18]

    # Use iloc to select columns by their numerical indices
    df = df.iloc[:, columns_to_keep].reset_index(drop=True)

    # Replace NaN values with "---"
    df.fillna("---", inplace=True)

    # Round the values in the last three columns to integers
    df.iloc[:, -3:] = df.iloc[:, -3:].round().astype(int)

    return df
