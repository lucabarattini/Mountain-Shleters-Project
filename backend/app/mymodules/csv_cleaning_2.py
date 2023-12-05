def cleancsv2(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Drop the first two columns
    df.drop(df.columns[0:2], axis=1, inplace=True)

    # List of column indices to keep
    columns_to_keep = [0, 1, 4, 7, 9, 12, 14, 15, 16]

    # Keep only the specified columns and reset the index
    df = df.iloc[:, columns_to_keep].reset_index(drop=True)

    # Shift the third column to the first place
    third_column = df.pop(df.columns[2])
    df.insert(0, third_column.name, third_column)

    # Replace NaN values with "---"
    df.fillna("---", inplace=True)

    # Rename the last three columns
    df.rename(columns={df.columns[-3]: "CAMERE", df.columns[-2]: "LETTI", df.columns[-1]: "BAGNI"}, inplace=True)

    return df