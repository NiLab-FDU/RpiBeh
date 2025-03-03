import numpy as np
from dlclive import DLCLive, Processor

from client_host.PostDetect import PostDetect
from client_host.Utils import get_largest_component_and_center, apply_mask


class DLCLiveModel(PostDetect):
    def __init__(self, controller, model_path, example_photo, area_type, area_points, key_points):
        super().__init__(controller, "DLCLiveModel")
        self.dlc_proc = Processor()
        self.dlc_live = DLCLive(model_path, processor=self.dlc_proc)
        self.dlc_live.init_inference(example_photo)
        self.area_type = area_type
        self.area_points = area_points
        self.key_points = key_points
        self.all_joints_names = self.dlc_live.cfg['all_joints_names']
        self.joint_likelihood_threshold = 0.9
        self.use_index = self.init_use_index()

    def init_use_index(self):
        use_index = []
        for i in range(len(self.all_joints_names)):
            if self.key_points[self.all_joints_names[i]]:
                use_index.append(i)
        return use_index

    def get_res(self, image):
        marked_frame = apply_mask(image[1], self.area_type, self.area_points)
        pose = self.dlc_live.get_pose(marked_frame)
        x, y = pose[self.use_index, :2].mean(0)
        res = [image[0], x, y]
        res.extend(pose.flatten())
        return [res]

    def get_x_y_by_pose(self, pose):
        # pose = pose[self.use_index][pose[self.use_index][:, 2] > self.joint_likelihood_threshold]
        return pose[self.use_index, :2].mean(0) if pose.size else (np.nan, np.nan)

    def get_dlc_use_index(self):
        return self.use_index


class TrackLiveModel(PostDetect):
    def __init__(self, controller, background, area_type, area_points):
        super().__init__(controller, "TrackLiveModel")
        self.background = background
        self.area_type = area_type
        self.area_points = area_points

    def get_res(self, image):
        difference, thresh_img, largest_contour, cX, cY = \
            get_largest_component_and_center(image[1], self.background, diff_type='div', div_coeff=5,
                                             thresh_type='manual', thresh=120, use_open_close=True,
                                             area_type=self.area_type, area_points=self.area_points)
        return [[image[0], cX, cY], difference, thresh_img, largest_contour]
