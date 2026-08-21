# ======================== Libraries ====================
import numpy as np
from vispy import app
import os
from SpiralSearch.Searcher import SpiralSearchClass
from SpiralSearch.Searcher import SpiralPropsClass
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import savgol_filter
from vispy.io import write_png
import tkinter as tk
from tkinter import ttk, messagebox

def choose_file(file_list):
    selected = None

    def on_select():
        nonlocal selected
        selection = listbox.curselection()
        if selection:
            selected = file_list[selection[0]]
            root.destroy()

    root = tk.Tk()
    root.title("Choose a CSV file")
    root.geometry("500x300")

    listbox = tk.Listbox(root, width=80, height=15)
    listbox.pack(padx=10, pady=10, fill="both", expand=True)

    for filename in file_list:
        listbox.insert(tk.END, filename)

    button = tk.Button(root, text="Select", command=on_select)
    button.pack(pady=10)

    root.mainloop()

    return selected

# ========================= Main code ==========================

if __name__ == '__main__':

    root_dir = Path(str(input('Specify the full paath for Cu data directory: ')).strip())
    analysis = True

    while analysis:
        files = [f for f in os.listdir(root_dir) if f.endswith('_CUdata.csv')]
        file = choose_file(files)
        if file is None:
            raise SystemExit("No CSV file selected.") 
        
        root = tk.Tk()
        root.withdraw()
        animation = messagebox.askokcancel('Confirm', 'Run animation?')
        par_file = messagebox.askokcancel('Confirm', 'Use the previous parameter file?')
        root.destroy()

        name = os.path.splitext(os.path.basename(str(file)))[0]
        folderpath = root_dir / name[:-10]
        folderpath.mkdir(exist_ok=True)
        subfolderpath = folderpath / name
        subfolderpath.mkdir(exist_ok=True)
        print(f"working on {subfolderpath}")

        filepath = root_dir / file
        S = SpiralSearchClass()
        S.read_file(filepath)
        S.find_center()

        if par_file:
            filename = name + '_Parameters.csv'
            filepath = subfolderpath / filename

            if filepath.is_file():
                S.read_parameters_from_file(filepath)
            else:
                raise SystemError(f"Parameter file not found: {filepath}.")
        else:
            # ========================== Parameters =================================
            S.SET_parameters(
                F1=0.003,          # [percentage of the heigh] thickness of the disc found at certain level 
                F2=0.15,            # [percentage of the radius] maximum radius of the points around the last centroid 
                F3=2000,            # number of levels
                F4=5,               # [degree] angle increment for centroid interpolation 
                F5=30,               # [degree] angle in centroid extrapolation where frame is incremented 
                F6=0.1,            # [percentage of the heigh] percentage of frame limit to centroid calculation without search functions 
                F7=0.1,             # [percentage of the radius] centroid maximum norm to be considered in the middle
                F8=0.0015,          # [percentage of the heigh] level jump for centroid extrapolation
                F9=0.005,           # [percentage of the heigh] levels to extrapolate a centroid directly upwards 
                F10=0.7,            # [degree] max angle of backward rotation allowed
                F11=2,              # wave search increment
                F12=60,            # [degree] cut angle
                F13=0.1            # [percentage of the heigh] minimum height percentage to find for a cut
                )
            # =======================================================================

        S.find_levels()    
        S.SET_graphics(5, 'yellow', 10, 'cyan', 1, 'black')
        if animation:
            S.run_animation(FPS=300)
        else:
            S.run_searcher()

        S.invert_spiral()

        P = SpiralPropsClass()
        P.spiral_points = S.coords
        P.smooth_sample(window=10)
        P.find_spiral_length(span=20)

        plt.figure(figsize=(10, 6))

        P.lead_angle()
        plt.plot(P.lead[:,0], P.lead[:,1])
        P.lead[:, 1] = savgol_filter(P.lead[:, 1], window_length=30, polyorder=3)
        plt.plot(P.lead[:,0], P.lead[:,1])
        P.lead[:, 1] = gaussian_filter1d(P.lead[:, 1], sigma=30)
        plt.plot(P.lead[:,0], P.lead[:,1])
        plt.ylim([0, 3*P.lead[:,1].max()])
        

        h = P.spiral_smoothed[-1, -1]
        elong = (P.spiral_length / h) * 100
        print(30*'=')
        print(f"Hight of zone 3 (mm) = {h:.2f}")
        print(f"Hight of zone 3 (%) = {(S.perc_h*100):.2f}")
        print(f"Spiral length = {P.spiral_length:.2f}")
        print(30*'=')
        
        if not animation:
            S.scatter.set_data(pos=S.CUdata, face_color='black', size=1, edge_color='black')
            S.scatter1.set_data(pos=S.coords, face_color='black', size=2, edge_color='yellow')
            S.scatter2.set_data(pos=P.spiral_smoothed, face_color='cyan', size=5, edge_color='cyan')
            S.canvas.update()
            S.view.camera.set_range(margin=0.1)
            app.run()

        plt.title('Spiral Lead Angle')
        plt.xlabel('Height [mm]')
        plt.ylabel('Lead angle [degree]')
        filename = name + '_Lead_Graph'
        filepath = subfolderpath / filename
        plt.savefig(filepath)
        plt.show()
        
        result = messagebox.askokcancel('Confirm', 'Do you want to save the results? (previous results may be overwritten)')
        if result:
            S.save_out(root=subfolderpath)

            filename = name + '_Results.csv'
            filepath = subfolderpath / filename
            out = np.array([[h, P.spiral_length]])
            np.savetxt(fname=filepath, X=out, delimiter=';', header='Zone_3_height;Spiral_length')

            filename = name + '_Smoothed_Spiral.csv'
            filepath = subfolderpath / filename
            np.savetxt(fname=filepath, X=P.spiral_smoothed, delimiter=';')

            filename = name + '_Lead_Angle.csv'
            filepath = subfolderpath / filename
            np.savetxt(fname=filepath, X=P.lead, delimiter=';')

            img_data = S.canvas.render(alpha=False)
            img = Image.fromarray(img_data)
            filename = name + '_scatter.jpg'
            filepath = subfolderpath / filename
            img.save(filepath, quality=95)
    
        analysis = messagebox.askokcancel('Confirm', 'Do you want to keep analysing the data?')
