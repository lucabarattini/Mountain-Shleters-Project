import pandas as pd

def process_data(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Drop the first two columns
    df.drop(df.columns[0:2], axis=1, inplace=True)

    # List of column indices to keep
    columns_to_keep = [0, 1, 4, 7, 9, 12, 14, 15, 16]

    # Keep only the specified columns and reset the index
    df = df.iloc[:, columns_to_keep].reset_index(drop=True)
    
    # Replace NaN values with "---"
    df.fillna("---", inplace=True)

    return df
