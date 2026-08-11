import csv
import numpy as np
from vispy import app, scene
# import imageio
import pandas as pd
from SpiralSearch.SpiralLinalg import *
import os

# [TODO] create separate class or functions for basic linear algebra for spirals

# pip intall numpy
# pip install vispy
# pip install PySide6
# pip install PyOpenGL PyOpenGL_accelerate


def create_folder(root, folder_name):
    folder_path = os.path.join(root, folder_name)
    os.makedirs(folder_path, exist_ok=True)

class SpiralSearchClass:
    def __init__(self):
        self.CUdata = None
        self.npoints = int
        self.mask = False
        self.Graph = np.array([])
        self.frame_count = 0
        self.coords = np.zeros((1,3), dtype=float)
        self.Zfloor = None
        self.Zheight = None
        self.Ywidth = None
        self.Xwidth = None
        self.levels = None
        self.center = None
        self.timer = None
        self.true_centroid = None
        self.r = None
        self.frames = []
        self.gifname = ""
        self.up_count = 0
        self.angle_search = 0
        self.angle_key = 0
        self.angle_amp = 0
        self.level_cut = False
        self.perc_h = float
        self.out = []
        self.filename = ''
        self.par_out = {}

    def store_out(self, output):
        self.out.append(output)
    
    def save_out(self, root):
        name = os.path.splitext(os.path.basename(str(self.filename)))[0]

        filepath = os.path.join(root, f"{name}.out")
        with open(filepath, "w") as file:
            for out in self.out:
                file.write(f"{out}\n")

        filepath = os.path.join(root, f"{name}_Parameters.csv")
        with open(filepath, "w") as f:
            for key, value in self.par_out.items():
                f.write(f"{key};{value}\n")

        filepath = os.path.join(root, f"{name}_Spiral_Points.csv")
        np.savetxt(filepath, self.coords, delimiter=";")

    def SET_parameters(self, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13):
        h = self.Zheight - self.Zfloor  # Height of the spiral
        self.f1 = F1*h                  # thickness of the disc found at certain level
        self.f2 = F2*self.r                  # maximum radius of the points around the last centroid
        self.f3 = F3                    # number of levels
        self.f4 = F4                    # angle increment for centroid interpolation
        self.f5 = F5                    # angle in centroid extrapolation where frame is incremented
        self.f6 = F6*F3                 # frame limit to centroid calculation without search functions 
        self.f7 = F7*self.r                  # centroid maximum norm to be considered in the middle
        self.f8 = F8                    # percentage of level jump for centroid extrapolation
        self.f9 = F9*F3                 # max number of levels to extrapolate a centroid directly upwards 
        self.f10 = F10                  # max angle of backward rotation allowed
        self.f11 = F11                  # wave search 
        self.f12 = F12                  # cut angle
        self.f13 = F13

        self.par_out = {'F1': F1,'F2': F2,'F3': F3, 'F4': F4,'F5': F5,'F6': F6,
                'F7': F7,'F8': F8,'F9': F9,'F10': F10,'F11': F11,'F12': F12, 'F13': F13}

    def read_parameters_from_file(self, filepath):
        parameters = []
        with open(filepath, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    parameters.append(str(line).strip().split(';')[-1])

        h = self.Zheight - self.Zfloor  # Height of the spiral
        self.f1 = float(parameters[0])*h
        self.f2 = float(parameters[1])*self.r
        self.f3 = int(parameters[2])
        self.f4 = int(parameters[3])
        self.f5 = int(parameters[4])
        self.f6 = float(parameters[5])*self.f3
        self.f7 = float(parameters[6])*self.r
        self.f8 = float(parameters[7])
        self.f9 = float(parameters[8])*self.f3
        self.f10 = float(parameters[9])
        self.f11 = int(parameters[10])
        self.f12 = int(parameters[11])
        self.f13 = float(parameters[12])

        self.par_out = {'F1': parameters[0],'F2': parameters[1],'F3': parameters[2], 'F4': parameters[3],
                        'F5': parameters[4],'F6': parameters[5], 'F7': parameters[6],'F8': parameters[7],
                        'F9': parameters[8],'F10': parameters[9],'F11': parameters[10],'F12': parameters[11],
                          'F13': parameters[12]}

    def SET_graphics(self, s1, c1, s2, c2, s3, c3):
        self.canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='gray')
        self.scatter = scene.visuals.Markers()
        self.scatter1 = scene.visuals.Markers()
        self.scatter2 = scene.visuals.Markers()
        self.scatter3 = scene.visuals.Markers()
        self.view = self.canvas.central_widget.add_view()
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)
        self.view.camera = 'turntable'
        self.view.add(self.scatter)
        self.view.add(self.scatter1)
        self.view.add(self.scatter2)
        self.view.camera.center = self.center  # Centraliza nos pontos
        self.spline_size = s1
        self.spline_color = c1
        self.level_size = s2
        self.level_color = c2
        self.CU_size = s3
        self.CU_color = c3

    def read_file(self, file):
        self.filename = file
        # Read CSV file and store values into a numpy matrix
        with open(self.filename, 'r') as f:
            reader = csv.reader(f)
            rawdata = list(reader)
        # Store csv data in a numpy matrix
        self.npoints = np.shape(rawdata)[0]
        self.CUdata = np.zeros((self.npoints, 3), dtype=float)
        for row in range(self.npoints):
            cols = str(rawdata[row][0]).split(";")
            self.CUdata[row, :] = ([float(cols[col]) for col in range(3)])

        
        self.Zheight = np.max(self.CUdata[:, 2])
        if self.Zheight > 1000:
            self.CUdata /= 1000
            self.Zheight = np.max(self.CUdata[:, 2])
        self.Zfloor = np.min(self.CUdata[:, 2])
        self.Ywidth = abs(np.max(self.CUdata[:, 1]) - np.min(self.CUdata[:, 1]))
        self.Xwidth = abs(np.max(self.CUdata[:, 0]) - np.min(self.CUdata[:, 0]))

        if self.Zheight > 1000:
            self.CUdata[:, 2] /= 1000

    def find_levels(self):
        self.levels = np.linspace(self.Zfloor, self.Zheight, int(self.f3))

    def find_center(self):
       # Find center
        self.center = np.mean(self.CUdata, axis=0)
        self.center[2] = self.Zfloor
        self.CUdata -= self.center
        self.center = np.mean(self.CUdata, axis=0)
        self.CUdata[-1, :] = self.center
        self.r = max(self.Xwidth, self.Ywidth)/2
        # update floor and heigth
        self.Zfloor = np.min(self.CUdata[:, 2])
        self.Zheight = np.max(self.CUdata[:, 2])


    def rotate(self, theta, vec):
        c = np.cos(theta)
        s = np.sin(theta)
        R = np.matrix([[c, -s],
                       [s, c]])
        rot = np.dot(R, vec)
        return rot

    def rotate3D(self, thetaX, thetaY, thetaZ):
        Rx = np.matrix([[1, 0, 0],
                        [0, np.cos(thetaX), -np.sin(thetaX)],
                        0, np.sin(thetaX), np.cos(thetaX)])
        Ry = np.matrix([[np.cos(thetaY), 0, np.sin(thetaY)],
                        [0, 1, 0],
                        -np.sin(thetaX), 0, np.cos(thetaX)])
        Rz = np.matrix([[0, np.cos(thetaX), -np.sin(thetaX)],
                        [0, np.sin(thetaZ), np.cos(thetaZ)],
                        0, 0, 1])
        R = Rz*Ry*Rx
        return R

    def find_disc(self, level, tol):
        self.mask = np.abs(self.CUdata[:, 2] - level) < tol

    def check_radius(self, centroid, r):
        # 1. Isolar apenas os pontos (X, Y) que estão atualmente na máscara
        # Usamos [:, :2] para pegar apenas as colunas X e Y
        pontos_ativos = self.CUdata[self.mask][:, :2]

        # 2. Calcular a distância Euclidiana de todos os pontos ao centroide de uma vez
        # A fórmula é: sqrt((x - xc)^2 + (y - yc)^2)
        distancias = np.linalg.norm(pontos_ativos - np.reshape(centroid[0,:2], (1,2)), axis=1)

        # 3. Identificar quais pontos ativos atendem à condição de remoção
        condicao_remover = distancias > r

        # 4. Mapear de volta para os índices originais e atualizar a self.mask para False
        # np.flatnonzero nos dá as posições reais dos pontos que estavam como True [cite: 375, 376]
        indices_originais = np.flatnonzero(self.mask)
        self.mask[indices_originais[condicao_remover]] = False

    def centroid_search(self, theta):
        a = self.coords[-1,:2]
        b = np.zeros((1,3), dtype=float)
        b[0,:2] = self.rotate(-theta, a)
        b[0,2] = self.levels[self.frame_count]
        return b

    def find_rotation(self, a, b):
        rot = a[0,0]*b[0,1] - a[0,1]*b[0,0]
        if rot >= 0:
            return True
        else:
            return False

    def centroid_angle(self, reference, centroid):
        a = np.reshape(centroid[0,:2], (1,2))
        b = np.reshape(reference[0,:2], (1,2))
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        dotab = np.dot(a, np.transpose(b))
        theta = np.arccos(dotab/(norm_a*norm_b))
        return theta

    def find_centroid(self):
        search_centroid = False 
        centroid_rot = False # centroid rotation
        middle_centroid = False
        # find disc in Z direction
        self.find_disc(self.levels[self.frame_count], self.f1) # crate a boolean mask for the original data
        mask_check = np.count_nonzero(self.mask) # check if any point was foud inside the disc
        if  mask_check != 0:
            centroid = np.mean(self.CUdata[self.mask], axis=0)[:2].reshape(1,2)
            if np.linalg.norm(centroid) <= self.f7:
                search_centroid = True
                middle_centroid = True
                self.store_out("Centroid is in the middle")
        # store coordinate of last centroid
        last_centroid = np.reshape(self.coords[-1,:], (1,3))
        # check distance of the point found from the last centroid
        self.check_radius(last_centroid, self.f2) # filters previous data
        # check if point cloud is forward from the centroid
        # [...]
        # check if any point was found within the centroid radio
        mask_check = np.count_nonzero(self.mask)
        
        if mask_check != 0 and search_centroid == False: # if some point was found
            self.angle_amp = 0
            self.store_out(f"Point close to the centroid found")
            # find the mean coordinate of the masked data
            centroid = np.mean(self.CUdata[self.mask], axis=0).reshape(1,3)
            # check rotation of the centroid from the last one
            centroid_rot = self.find_rotation(last_centroid, centroid) # True: anti-clockwise, False: clockwise
            if centroid_rot:
                self.store_out("Centroid rotated backward")
                rot_theta = np.rad2deg(self.centroid_angle(reference=centroid, centroid=last_centroid))
                if rot_theta <= self.f10:
                    self.store_out(f"True centroid found with backwards rotation of {rot_theta}")
                    self.true_centroid = centroid
                    self.frame_count += 1
                else:
                    if self.up_count <= self.f9:
                        self.store_out("upward extrapolation")
                        centroid = last_centroid # extrapolate centroid upwards
                        self.up_count += 1
                    else:
                        self.store_out("forward extrapolation")
                        self.up_count = 0
                        theta = np.deg2rad(self.f4)
                        centroid = self.centroid_search(theta) # centroid extrapolation
                    self.frame_count += 1
                    centroid[0, 2] = self.levels[self.frame_count]
                
            else:
                self.store_out("True centroid found")
                self.true_centroid = centroid
                self.frame_count += 1

        elif mask_check == 0 or search_centroid: # no point around the last centroid was found or centroid search was activated
            self.store_out('--------------------------------')
            self.store_out('>> Centroid search activated <<')
            self.store_out('--------------------------------')
            theta = np.deg2rad(self.f4)
            centroid = self.centroid_search(theta) # centroid extrapolation
            angle = self.centroid_angle(self.true_centroid, centroid)
            self.store_out(f"Extrapolation {np.rad2deg(angle)}° far from last true centroid")
            self.perc_h = self.levels[self.frame_count]/self.Zheight
            zone_cut = False

            if middle_centroid:
                    if np.rad2deg(angle) > self.f12 and self.perc_h > self.f13:
                        self.store_out(f"Angle of extrapolation exceeded {self.f12}°, centroid search will be finished")
                        self.level_cut = True
                    self.frame_count += 1
                    centroid[0, 2] = self.levels[self.frame_count]

            elif not zone_cut:
                if np.rad2deg(angle) > self.f5:
                    self.store_out('--------------------------------')
                    self.store_out('>> Wave search activated <<')
                    self.store_out('--------------------------------')
                    self.angle_search += 1
                    jump = int(self.f8*self.f3)
                    if jump < 1: # the lowest jump increment should be 1
                        jump = 1
                    self.store_out(f"Angle of extrapolation exceeded {self.f5}°, {jump} levels will be increased")
                    
                    if self.angle_search <= (1+self.angle_amp):
                        factor = ((-1)**self.angle_key)
                        self.store_out(f"Wave factor = {factor}")
                        self.frame_count = self.frame_count + factor*jump
                    else:
                        self.angle_amp += self.f11
                        self.angle_key += 1
                        self.angle_search = 0
                    centroid[0, 2] = self.levels[self.frame_count]
            else:
                self.frame_count = np.size(self.levels) # end of the animation
            self.store_out(f"Extrapolation at {100*self.perc_h:.2f}% of the height")
        return centroid

    def run_animation(self, FPS):
        self.store_out('================================')
        self.store_out('        Spiral Search 1.0       ')
        self.store_out('================================')
        self.timer = app.Timer(interval=(1/FPS), connect=self.on_timer_update, start=True)
        app.run()

    def run_searcher(self):
        self.store_out('================================')
        self.store_out('        Spiral Search 1.0       ')
        self.store_out('================================')
        running = True
        while running:
            if self.frame_count == 0:
                self.find_disc(self.levels[self.frame_count], self.f1)
                centroid = np.mean(self.CUdata[self.mask], axis=0).reshape(1,3)
                self.true_centroid = centroid
                self.coords[0,:] = centroid
                # update frame count
                self.frame_count += 1

            elif 0 < self.frame_count and self.frame_count < self.f6:
                self.find_disc(self.levels[self.frame_count], self.f1)
                mask_check = np.count_nonzero(self.mask)
                if mask_check != 0:
                    centroid = np.mean(self.CUdata[self.mask], axis=0).reshape(1,3)
                    self.true_centroid = centroid
                    self.coords = np.append(self.coords, centroid, axis=0)
                elif self.f6 == (self.frame_count + 1):
                    self.f6 += 2
                # update frame count
                self.frame_count += 1

            elif self.f6 <= self.frame_count and self.frame_count < (np.size(self.levels)-1):
                if self.level_cut:
                    self.store_out("Spiral search finished")
                    running = False
                centroid = self.find_centroid()
                self.coords = np.append(self.coords, centroid, axis=0)
            else:
                self.store_out("Spiral search finished")
                running = False
    
    def on_timer_update(self, ev):
        self.store_out(f"Frame {self.frame_count}")
        if self.frame_count == 0:
            self.store_out('First centrois calculation')
            self.find_disc(self.levels[self.frame_count], self.f1)
            centroid = np.mean(self.CUdata[self.mask], axis=0).reshape(1,3)
            self.true_centroid = centroid
            self.coords[0,:] = centroid
            # update canvas
            self.scatter.set_data(pos=self.CUdata, face_color=self.CU_color, size=self.CU_size)
            self.scatter1.set_data(pos=self.CUdata[self.mask], face_color=self.level_color, size=self.level_size)
            self.scatter2.set_data(pos=self.coords, face_color=self.spline_color, size=self.spline_size)
            self.canvas.update()
            self.view.camera.set_range()
            # update frame count
            self.frame_count += 1

        elif 0 < self.frame_count and self.frame_count < self.f6:
            self.store_out('No centroid search mechanisms are being used')
            self.find_disc(self.levels[self.frame_count], self.f1)
            mask_check = np.count_nonzero(self.mask)
            if mask_check != 0:
                centroid = np.mean(self.CUdata[self.mask], axis=0).reshape(1,3)
                self.true_centroid = centroid
                self.coords = np.append(self.coords, centroid, axis=0)
            elif self.f6 == (self.frame_count + 1):
                self.f6 += 2
            # update canvas
            self.scatter1.set_data(pos=self.CUdata[self.mask], face_color=self.level_color, size=self.level_size)
            self.scatter2.set_data(pos=self.coords, face_color=self.spline_color, size=self.spline_size)
            self.canvas.update()
            # update frame count        
            self.frame_count += 1

        elif self.f6 <= self.frame_count and self.frame_count < (np.size(self.levels)-1):
            if self.level_cut:
                self.canvas.update()
                self.store_out("Animation finished")
                self.timer.stop()
            else:
                centroid = self.find_centroid()
                self.coords = np.append(self.coords, centroid, axis=0)
                # update canvas
                self.scatter1.set_data(pos=self.CUdata[self.mask], face_color=self.level_color, size=self.level_size)
                self.scatter2.set_data(pos=self.coords, face_color=self.spline_color, size=self.spline_size)
                self.canvas.update()
        else:            
            self.store_out("Animation finished")
            self.timer.stop()
    
    # def export_gif(self):
    #     self.store_out(f"A gerar GIF com {len(self.frames)} frames... aguarde.")
    #     # O parâmetro 'fps' define a velocidade de reprodução
    #     imageio.mimsave(self.gifname, self.frames, fps=15)
    #     self.store_out(f"GIF guardado com sucesso como {self.gifname}!")

    def invert_spiral(self, spline_invert=True):
        self.CUdata[:,-1] = abs(self.CUdata[:,-1] - self.Zheight)
        if spline_invert:
            self.coords[:,-1] = abs(self.coords[:,-1] - self.Zheight)

class SpiralPropsClass:
    def __init__(self):
        self.spiral_points = []
        self.spiral_smoothed = []
        self.spiral_length = 0.0
        self.theta = []
        self.lead = []

    def read_spiral(self, filename):
        self.spiral_points = pd.read_csv(filepath_or_buffer=filename, delimiter=';').to_numpy(dtype=float).copy()

    def find_spiral_length(self, span):
        self.spiral_length = 0.0
        for step in range(0, len(self.spiral_points)-span, span):
            sample = self.spiral_smoothed[step:(step+span), :]
            self.spiral_length += self.estimate_arc_with_path(sample_points=sample)
            # dtheta = self.centroid_angle(sample[0, :], sample[-1, :])
            # dz = sample[-1, -1] - sample[0, -1]
            # lead = np.arctan(dz / (1 * dtheta))
        return
    
    def estimate_arc_with_path(self, sample_points):
        pts = np.asarray(sample_points)
        # Euclidean path length (true curve length)
        diffs = np.diff(pts, axis=0)
        segment_lengths = np.linalg.norm(diffs, axis=1)
        path_length = np.sum(segment_lengths)
        return path_length

    def smooth_sample(self, window=5):
        self.spiral_smoothed = np.copy(self.spiral_points)
        for i in range(len(self.spiral_points)):
            i_min = max(0, i - window)
            i_max = min(len(self.spiral_points), i + window)
            self.spiral_smoothed[i] = self.spiral_points[i_min:i_max].mean(axis=0)
        return
            
    def build_angle(self):
        ref = self.spiral_smoothed[-1, :2]
        self.theta = np.reshape([angle(dim=2, point1=ref, point2=point) for point in self.spiral_smoothed[:, :2]], (len(self.spiral_smoothed)))

    def lead_angle(self):
        self.build_angle()
        self.lead = np.zeros((len(self.theta)-1, 2), dtype=float)
        for i in range(1, len(self.theta)):
            T = [(self.spiral_smoothed[i, j]-self.spiral_smoothed[i-1, j])/(self.theta[i]) for j in range(3)]
            self.lead[i-1, 1] = np.atan(T[-1]/np.sqrt((T[0]**2 + T[1]**2)))
            if np.isnan(self.lead[i-1, 1]) and i > 1:
                self.lead[i-1, 1] = self.lead[i-2, 1]
            self.lead[i-1, 0] = (self.spiral_smoothed[i, 2] + self.spiral_smoothed[i-1, 2]) / 2
            self.lead[i-1, 1] = abs(np.rad2deg(self.lead[i-1, 1]))

        if self.lead[:, 0].max() > 1000:
            self.lead[:, 0] /= 1000

    def lead_angle_span(self, span):
        nsamples = int(len(self.spiral_smoothed)/span)
        self.lead = np.zeros((nsamples, 2), dtype=float)
        # samplelead = np.zeros((span), dtype=float)
        count = 0
        for step in range(0, (len(self.spiral_smoothed)-span), span):
            sample = self.spiral_smoothed[step:(step+span), :]
            dtheta = angle(dim=2, point1=sample[0, :2], point2=sample[-1, :2]) # angle between the first and last points
            T = [(sample[0, j]-sample[-1, j])/(dtheta) for j in range(3)] 
            self.lead[count, 0] = np.mean([sample[0, 0],sample[-1, 0]]) # mean sample height
            self.lead[count, 1] = np.atan(T[-1]/np.sqrt((T[0]**2 + T[1]**2)))[0,0] # mean sample lead
            self.lead[count, 1] = np.rad2deg(self.lead[count, 1])
            count+=1

            # for i range(len(sample)):
            #     idtheta = angle(dim=2, point1=sample[i, j], point2=sample[i-1, j])
            #     T = [(sample[i, j]-sample[i-1, j])/(idtheta) for j in range(3)]
            #     samplelead[i] = np.atan(T[-1]/np.sqrt((T[0]**2 + T[1]**2)))
            # self.lead[step, 0] = np.mean(sample[:,0]) # mean of sample heights
            # self.lead[step, 1] = np.mean(samplelead) # mean of sample lead angles 

        if self.lead[:, 0].max() > 1000:
            self.lead[:, 0] /= 1000
            


        
