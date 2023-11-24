import pandas as pd

def clean_csv(file_path):
    """
    Cleans the specified CSV file and returns the cleaned DataFrame.

    Args:
    file_path (str): The path to the CSV file to be cleaned.

    Returns:
    pandas.DataFrame: The cleaned DataFrame.
    """

    # Load the data from a CSV file, using semicolon as the separator
    df = pd.read_csv(file_path, sep=';')

    # Drop the second column and columns from index 8 to 21 in one step to remove irrelevant data
    df.drop(columns=[df.columns[1]] + df.columns[8:22].tolist(), inplace=True)

    # Extract the new header (row at index 3) and drop the first four rows as they don't contain actual data
    new_header = df.iloc[3]
    df = df.iloc[4:]

    # Set the new header to properly name the columns
    df.columns = new_header

    # Drop rows where all values are NaN as they don't provide useful information
    df.dropna(how='all', inplace=True)

    # Substitute all NaN values with '---' to indicate missing data
    df.fillna('---', inplace=True)

    # Filter out rows where the first column starts with 'Rifugio' but is not 'Rifugio Passo di Vizze'
    df = df[~(df['Rifugio'].str.startswith('Rifugio') & (df['Rifugio'] != 'Rifugio Passo di Vizze'))]

    # Reset the index to ensure it is in sequential order after the rows have been dropped and filtered
    df.reset_index(drop=True, inplace=True)

    return df

