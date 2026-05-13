import numpy as np
from vispy import app
import os
import SpiralSearch as SPSRC

if __name__ == '__main__':
    root = "C:/GIT/HereonCodes/SpiralSearch/raw_data"
    csv_files = [f for f in os.listdir(root) if f.endswith('_CUdata.csv')]

    file_count = 0

    file = csv_files[10]

    filename = os.path.join(root, file)

    S = SPSRC.SpiralSearch()
    S.read_file(filename)
    S.find_center()
    S.SET_parameters(0.005, 0.05, 1000, 5, 100, 10, 0.05, 0.001)
    S.find_levels()
    S.SET_graphics(10, 'cyan', 10, 'yellow', 1, 'black')
    S.run_animation(600)
    app.run()

