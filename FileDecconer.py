import pandas 
import numpy as np
import os

# pip intall pandas
# pip install openpyxl

def create_folder(root, folder_name):
    folder_exists = os.path.exists(os.path.join(root, folder_name))
    if folder_exists:
        pass
    else:
        os.mkdir(os.path.join(root, folder_name))
    return

root = "E:\\BB-Camila\\07-Cu_dispersion_data"

foldername = 'CSV_files'
create_folder(root, foldername)

xlsx_files = [f for f in os.listdir(root) if f.endswith('.xlsx')]

for file in xlsx_files:

    f = os.path.join(root, file)

    # Read the Excel file
    df = pandas.read_excel(f)

    # Create a numpy matrix from the DataFrame
    matrix = df.values

    # Get the dimensions
    rows, cols = matrix.shape
    # create empty matrix to store processed data
    data = np.zeros((rows, cols), dtype=float)

    # index=False remove o primeiro elemento (o índice da linha)
    count_row = 0
    for row in df.itertuples(index=False):
        count_col = 0
        for col in row:
            data[count_row][count_col] = float(str(col).replace(",", "."))
            count_col += 1
        count_row += 1

    # Save data to CSV file with semicolon delimiter
    
    filename = file.split(".")[0] + "_CUdata.csv"
    filepath = os.path.join(foldername, filename)
    np.savetxt(os.path.join(root, filepath), data, delimiter=";")
    print(f"{filepath} saved successfully: {rows} rows x {cols} columns")