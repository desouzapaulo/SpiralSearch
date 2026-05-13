import numpy as np
from vispy import app
import os
import SpiralSearch as SPSRC

if __name__ == '__main__':
    root = "C:/GIT/HereonCodes/SpiralSearch/raw_data"
    raw_files = [f for f in os.listdir(root)]

    f1 = 0.005  # thickness of the disc found at certain level
    f2 = 0.05   # maximum radius of the points aroud the last centroid
    f3 = 1000   # number of levels
    f4 = 5      # angle increment for centroid interpolation
    f5 = 100    # angle in centroid extrapolation where frame is incremented
    f6 = 10     # frame limit to centroid calculation without search functions
    f7 = 0.05   # centroid maximum norm to be considered in the midle

    file = os.path.join(root, raw_files[10])
    S1 = SPSRC.SpiralSearch()
    S1.read_file(file)
    S1.find_center()
    S1.SET_parameters(f1, f2, f3, f4, f5, f6, f7)
    S1.find_levels()
    S1.SET_graphics(10, 'cyan', 10, 'yellow', 1, 'black')
    S1.find_spiral()
    S1.disp_data()
    L = S1.spiral_length()
    print(f"file: {raw_files[10]}")
    print(f"Spiral Lenght: {L:.2f}")

    file = os.path.join(root, raw_files[11])
    S2 = SPSRC.SpiralSearch()
    S2.read_file(file)
    S2.find_center()
    S2.SET_parameters(f1, f2, f3, f4, f5, f6, f7)
    S2.find_levels()
    S2.SET_graphics(10, 'cyan', 10, 'yellow', 1, 'black')
    S2.find_spiral()
    S2.disp_data()
    L = S2.spiral_length()
    print(f"file: {raw_files[11]}")
    print(f"Spiral Lenght: {L:.2f}")

    file = os.path.join(root, raw_files[12])
    S3 = SPSRC.SpiralSearch()
    S3.read_file(file)
    S3.find_center()
    S3.SET_parameters(f1, f2, f3, f4, f5, f6, f7)
    S3.find_levels()
    S3.SET_graphics(10, 'cyan', 10, 'yellow', 1, 'black')
    S3.find_spiral()
    S3.disp_data()
    L = S3.spiral_length()
    print(f"file: {raw_files[12]}")
    print(f"Spiral Lenght: {L:.2f}")

    app.run()

