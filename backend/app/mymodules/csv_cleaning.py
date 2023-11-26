import pandas as pd

def cleancsv1(file_path):
    """
    Cleans the specified CSV file 'egpie-RifugiOpenDa_2296-all.csv' and returns the cleaned DataFrame.

    Args:
    file_path (str): The path to the CSV file to be cleaned.

    Returns:
    pandas.DataFrame: The cleaned DataFrame.
    """
    # Load the data
    df = pd.read_csv(file_path, sep=';')

    # Combining ranges and specific columns to drop into a single list
    columns_to_drop = list(range(0, 6)) + [8, 9, 11, 40, 41] + list(range(12, 39))

    # Dropping the specified columns inplace
    df.drop(df.columns[columns_to_drop], axis=1, inplace=True)

    # Dropping all columns after the 5th column
    df = df.iloc[:, :5]

    # Rename the 4th and 5th columns
    df.rename(columns={df.columns[3]: 'nr. camere', df.columns[4]: 'nr. letti'}, inplace=True)

    # Substitute NaN values and zeros with '---'
    df.replace({pd.NA: '---', 0: '---'}, inplace=True)

    # Convert numbers in 'nr. camere' and 'nr. letti' to integers
    for col in ['nr. camere', 'nr. letti']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna('---').astype(str).str.replace('.0', '')
    
    return df