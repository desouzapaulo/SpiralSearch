import csv
import numpy as np
from vispy import app, scene
import os
import imageio

# pip intall numpy
# pip install vispy
# pip install PySide6
# pip install PyOpenGL PyOpenGL_accelerate

class SpiralSearch:
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

    def SET_parameters(self, F1, F2, F3, F4, F5, F6, F7, F8):
        h = self.Zheight - self.Zfloor # Height of the spiral
        self.f1 = F1*h  # thickness of the disc found at certain level
        self.f2 = F2*h  # maximum radius of the points aroud the last centroid
        self.f3 = F3    # number of levels
        self.f4 = F4    # angle increment for centroid interpolation
        self.f5 = F5    # angle in centroid extrapolation where frame is incremented
        self.f6 = F6    # frame limit to centroid calculation without search functions 
        self.f7 = F7*h  # centroid maximum norm to be considered in the midle
        self.f8 = F8    # percentage of level jump for centroid extrapolation

    def SET_graphics(self, s1, c1, s2, c2, s3, c3):
        self.canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='gray')
        self.scatter = scene.visuals.Markers()
        self.scatter1 = scene.visuals.Markers()
        self.scatter2 = scene.visuals.Markers()
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

    def read_file(self, filename):
        # Read CSV file and store values into a numpy matrix
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            rawdata = list(reader)
        # Store csv data in a numpy matrix
        self.npoints = np.shape(rawdata)[0]
        self.CUdata = np.zeros((self.npoints, 3), dtype=float)
        for row in range(self.npoints):
            cols = str(rawdata[row][0]).split(";")
            self.CUdata[row, :] = ([float(cols[col]) for col in range(3)])

        self.Zfloor = np.min(self.CUdata[:, 2])
        self.Zheight = np.max(self.CUdata[:, 2])
        self.Ywidth = abs(np.max(self.CUdata[:, 1]) - np.min(self.CUdata[:, 1]))
        self.Xwidth = abs(np.max(self.CUdata[:, 0]) - np.min(self.CUdata[:, 0]))


    def find_levels(self):
        self.levels = np.linspace(self.Zfloor, self.Zheight, self.f3)

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
        centroid_rot = False
        # find disc in Z direction
        self.find_disc(self.levels[self.frame_count], self.f1) # crate a boolean mask for the original data
        # check if any point was foud inside the disc
        mask_check = np.count_nonzero(self.mask)
        if  mask_check != 0:
            centroid = np.mean(self.CUdata[self.mask], axis=0)[:2].reshape(1,2)
            if np.linalg.norm(centroid) <= self.f7:
                search_centroid = True
                print("Centroid is in the middle")
        # store coordinate of last centroid
        last_centroid = np.reshape(self.coords[-1,:], (1,3))
        # check distance of the point found from the last centroid
        self.check_radius(last_centroid, self.f2) # filters previous data
        # check if point cloud is forward from the centroid
        # [...]
        # check if any point was foud within the centroid radio
        mask_check = np.count_nonzero(self.mask)
        
        if  mask_check != 0 and search_centroid == False: # if some point was found
            # print(f"Point close to the centroid found successfully for frame {self.frame_count}")
            # find the mean coordinate of the masked data
            centroid = np.mean(self.CUdata[self.mask], axis=0).reshape(1,3)
            # check rotation of the centroid from the last one
            centroid_rot = self.find_rotation(last_centroid, centroid) # True: anti-clockwise, False: clockwise
            if centroid_rot:
                print("Centroid rotated beckwards")
                # print(f"Centroid found in Anti-clockwise direction from last centroid for frame {self.frame_count}")
                theta = np.deg2rad(self.f4)
                centroid = last_centroid
                self.frame_count += 1
                centroid[0, 2] = self.levels[self.frame_count]
            else:
                print("True centroid found")
                self.true_centroid = centroid
                self.frame_count += 1
        elif mask_check == 0 or search_centroid: # no point aroud the last centroid was found
            print("Centroid search activated")
            theta = np.deg2rad(self.f4)
            centroid = self.centroid_search(theta)
            angle = self.centroid_angle(self.true_centroid, centroid)
            print(f"Extrapolation {np.rad2deg(angle)}° far from last true centroid")
            if angle > np.deg2rad(self.f5):
                jump = int(self.f8*self.f3)
                print(f"Angle of extrapolation exceeded {self.f5}°, {jump} levels will be increased")
                if (self.frame_count + jump) < self.f3:
                    self.frame_count += jump
                    centroid[0, 2] = self.levels[self.frame_count]
                else:
                    self.frame_count += 1
                    centroid[0, 2] = self.levels[self.frame_count]
                    
        return centroid

    def run_animation(self, FPS):
        print('\n\n', 30*'=','Spiral Search 1.0', 30*'='),
        self.timer = app.Timer(interval=(1/FPS), connect=self.on_timer_update, start=True)

    def find_spiral(self):
        print('\n\n', 30*'=','Spiral Search 1.0', 30*'=')
        frame = True
        while frame:
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
                if self.frame_count > 0 and self.frame_count % 100 == 0:
                    print('opa')

            elif self.f6 <= self.frame_count and self.frame_count < (np.size(self.levels)-1):
                centroid = self.find_centroid() # frame update happens inside this function
                self.coords = np.append(self.coords, centroid, axis=0)

            else:
                print("Spiral search finished")
                frame = False
                
    def on_timer_update(self, ev):
        if self.frame_count == 0:
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
            centroid = self.find_centroid()
            self.coords = np.append(self.coords, centroid, axis=0)
            # update canvas
            self.scatter1.set_data(pos=self.CUdata[self.mask], face_color=self.level_color, size=self.level_size)
            self.scatter2.set_data(pos=self.coords, face_color=self.spline_color, size=self.spline_size)
            if np.isclose((self.frame_count%10), 0):
                frame = self.canvas.render()
                self.frames.append(frame) 
            self.canvas.update()
        else:
            print("Animation finished")
            self.timer.stop()
            # self.export_gif()

    def spiral_length(self):
        S = [np.linalg.norm((self.coords[i+1]-self.coords[i])) for i in range(np.shape(self.coords)[0]-1)]
        s = np.sum(S)
        return s
    
    def export_gif(self):
        print(f"A gerar GIF com {len(self.frames)} frames... aguarde.")
        # O parâmetro 'fps' define a velocidade de reprodução
        imageio.mimsave(self.gifname, self.frames, fps=15)
        print(f"GIF guardado com sucesso como {self.gifname}!")
    
    def disp_data(self):
        # self.scatter.set_data(pos=self.CUdata, face_color=self.CU_color, size=self.CU_size)
        # self.scatter1.set_data(pos=self.CUdata[self.mask], face_color=self.level_color, size=self.level_size)
        self.scatter2.set_data(pos=self.coords, face_color=self.spline_color, size=self.spline_size)
        self.canvas.update()
        # self.view.camera.set_range()
    
    def smooth_arc(self, span):
        for step in range(np.shape(self.coords)[0]-span):
            sample = self.coords[step:(step+span), :2].reshape(1,2)
            R = np.mean(np.linalg.norm(sample))


        return 0
    
    def src_length(self, span):
        for step in range(np.shape(self.coords)[0]-span, span):
            sample = self.coords[step:(step+span), :]
            delta_theta = self.centroid_angle(sample[0, :], sample[-1, :])
        return 0
        