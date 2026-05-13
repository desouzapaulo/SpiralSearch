import csv
import numpy as np
from vispy import app, scene
import os
import imageio
import SpiralSearch as SPSRC

if __name__ == '__main__':
    root = "C:/GIT/HereonCodes/SpiralSearch/raw_data"
    csv_files = [f for f in os.listdir(root) if f.endswith('_CUdata.csv')]

    file_count = 0

    file = csv_files[2]

    filename = os.path.join(root, file)

    S = SPSRC.SpiralSearch()
    S.read_file(filename)
    S.find_center()
    S.SET_parameters(0.005, 0.05, 1000, 5, 100, 10, 0.05)
    S.find_levels()
    S.find_spiral()
    L = S.sipiral_lenght()
    print(f"file: {file}")
    print(f"Spiral Lenght: {L:.2f}")

