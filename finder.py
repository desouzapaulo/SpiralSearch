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