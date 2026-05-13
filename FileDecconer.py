import pandas 
import numpy as np
import os

# pip intall pandas
# pip install openpyxl

root = "C:/GIT/HereonCodes/SpiralSearch/raw_data"

xlsx_files = [f for f in os.listdir(root) if f.endswith('.xlsx')]

for file in xlsx_files:
    filename = os.path.join(root, file)

    # Read the Excel file
    df = pandas.read_excel(filename)

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
    csvname = file.split(".")[0] + "_CUdata.csv"
    np.savetxt(os.path.join(root, csvname), data, delimiter=";")
    print(f"{csvname} saved successfully: {rows} rows x {cols} columns")