import threading

import numpy as np

from client_host.Utils import get_largest_component_and_center, point_in_area

if 1:
    from client_host.DataBuffer import DataBuffer


class PostDetect(object):
    def __init__(self, controller, name, delay=0, duration=0):
        self.use_dlc = False
        self.controller = controller
        self.process_name = name
        self.last_res = False
        self.first_res_time = None
        self.gpio_state = False
        self.delay = delay
        self.duration_zero = duration == 0

    def get_res(self, input_data):
        return False

    def detector_record_thread(self, input_buffer: "DataBuffer", output_buffer: "DataBuffer", get_last_data=True):
        input_buffer_reader_index = input_buffer.register_reader()
        while True:
            if get_last_data:
                index, data = input_buffer.get_last_data(input_buffer_reader_index)
            else:
                index, data = input_buffer.get_data(input_buffer_reader_index)
            if index is None:
                output_buffer.add_data(None)
                break
            if data is None:
                continue
            out = self.get_res(data)
            output_buffer.add_data([index, out])
        print(f"{self.process_name} thread Finish")

    def start_record(self, input_buffer: "DataBuffer", output_buffer: "DataBuffer"):
        self.clear_params()
        thread = threading.Thread(target=self.detector_record_thread, args=(input_buffer, output_buffer))
        thread.start()

    def get_params(self):
        return {}

    def set_use_DLC(self, use):
        self.use_dlc = use

    def clear_params(self):
        self.first_res_time = None
        self.gpio_state = False

    def close(self):
        pass

    def close_loop_control(self, res, current_time):
        if self.duration_zero:
            if res and not self.gpio_state:
                self.controller.rpi_camera.gpio_up()
                self.gpio_state = True
            elif not res and self.gpio_state:
                self.controller.rpi_camera.gpio_down()
                self.gpio_state = False
        else:
            if res:
                if self.first_res_time is None:
                    self.first_res_time = current_time
                if (not self.gpio_state) and current_time - self.first_res_time >= self.delay:
                    self.controller.rpi_camera.gpio_start()
                    self.gpio_state = True
            else:
                self.first_res_time = None
                if self.gpio_state:
                    self.controller.rpi_camera.gpio_stop()
                    self.gpio_state = False


class DetectPosition(PostDetect):
    def __init__(self, controller, delay, duration):
        super().__init__(controller, "DetectPosition", delay, duration)
        area_type, area_points = controller.config_manager.get_settings_position_parameters()
        self.area_type = area_type
        self.area_points = area_points
        self.use_close_loop = (controller.config_manager.get_close_loop_method() == 'Position')

    def get_res(self, input_data):
        input_data = input_data[1][0]
        current_time, x, y = input_data[0], input_data[1], input_data[2]
        if np.isnan(x) or np.isnan(y):
            return [[False]]
        try:
            res = point_in_area(self.area_type, self.area_points, x, y)
            if self.use_close_loop:
                self.close_loop_control(res, current_time)
            return [[res]]
        except Exception:
            return [[False]]


class DetectFreezing(PostDetect):

    def __init__(self, controller, fps, delay, duration):
        super().__init__(controller, "DetectFreezing", delay, duration)
        th, dur = controller.config_manager.get_detection_threshold_and_dur('freezing')
        self.area_type, self.area_points = controller.config_manager.get_region_of_interest_area()
        self.dur_time = dur
        self.threshold = th
        self.fps = fps
        self.over_th_frame_num = max(int(self.dur_time * self.fps), 1)

        self.last_frame = None
        self.count_over_frame_num = 0
        self.use_close_loop = (controller.config_manager.get_close_loop_method() == 'Freezing')

        print(f"DetectFreezing Params\n"
              f"threshold: {self.threshold}\n"
              f"fps: {self.fps}\n"
              f"dur time: {self.dur_time}\n"
              f"over th frame num: {self.over_th_frame_num}")

    def clear_params(self):
        self.last_frame = None
        self.count_over_frame_num = 0

    def get_res(self, input_data):
        current_time, input_data = input_data[0], input_data[1]
        if self.last_frame is None:
            self.last_frame = input_data
            return [[False, False, np.nan]]

        try:
            _, thresh_img, _, _, _ = \
                get_largest_component_and_center(input_data, self.last_frame, diff_type='div', div_coeff=5,
                                                 thresh_type='manual', thresh=120, use_open_close=True, get_edge=False,
                                                 area_type=self.area_type, area_points=self.area_points)
            area_sum = np.sum(thresh_img) / 255.0 / thresh_img.shape[0] / self.last_frame.shape[1]
            over_th = area_sum < self.threshold
            if over_th:
                self.count_over_frame_num += 1
            else:
                self.count_over_frame_num = 0
            res = self.count_over_frame_num >= self.over_th_frame_num

            if self.use_close_loop:
                self.close_loop_control(res, current_time)

            self.last_frame = input_data
            return [[res, over_th, area_sum]]
        except Exception:
            self.last_frame = input_data
            return [[False, False, np.nan]]

    def get_params(self):
        return [self.threshold, self.fps, self.over_th_frame_num]


class DetectSpeed(PostDetect):
    def __init__(self, controller, fps, delay, duration):
        super().__init__(controller, "DetectSpeed", delay, duration)
        th, dur = controller.config_manager.get_detection_threshold_and_dur('speed')
        self.XY_Smooth_window_size, self.smooth_window_size = controller.config_manager.get_detection_smooth('speed')
        self.dur_time = dur
        self.th = th
        self.scale = controller.config_manager.get_scale()
        self.direction_over = controller.config_manager.get_speed_direction_over()
        self.first_over_th_time = None
        self.last_x = None
        self.last_y = None
        self.last_time = None
        self.speed_buffer = []
        self.xy_buffer = []

        self.use_close_loop = (controller.config_manager.get_close_loop_method() == 'Speed')
        print(f"DetectSpeed Params:\n"
              f"threshold: {self.th}")

    def clear_params(self):
        self.last_x = None
        self.last_y = None
        self.last_time = None
        self.first_over_th_time = None
        self.speed_buffer = []
        self.xy_buffer = []

    def get_res(self, input_data):
        input_data = input_data[1][0]
        current_time, x, y = input_data[0], input_data[1], input_data[2]
        if self.XY_Smooth_window_size > 0:
            self.xy_buffer.append([x, y])
            if len(self.xy_buffer) > self.XY_Smooth_window_size:
                self.xy_buffer.pop(0)
            x, y = np.nanmedian(np.array(self.xy_buffer), 0)
        if np.isnan(x) or np.isnan(y) or self.last_x is None or self.last_y is None:
            self.last_x, self.last_y, self.last_time = x, y, current_time
            return [[False, False, np.nan]]
        try:
            speed = self.scale * np.sqrt((x - self.last_x) * (x - self.last_x) + (y - self.last_y) * (y - self.last_y))
            speed /= (current_time - self.last_time)
            if self.smooth_window_size > 0:
                self.speed_buffer.append(speed)
                if len(self.speed_buffer) > self.smooth_window_size:
                    self.speed_buffer.pop(0)
                speed = np.nanmedian(self.speed_buffer)

            if self.direction_over:
                over_th = speed > self.th
            else:
                over_th = speed <= self.th

            res = False
            if over_th:
                if self.first_over_th_time is None:
                    self.first_over_th_time = current_time
                if current_time - self.first_over_th_time >= self.dur_time:
                    res = True
            else:
                self.first_over_th_time = None

            if self.use_close_loop:
                self.close_loop_control(res, current_time)

            self.last_x, self.last_y, self.last_time = x, y, current_time
            return [[res, over_th, speed]]
        except Exception:
            return [[False, False, np.nan]]

    def get_params(self):
        return [self.th]


class DetectAcceleration(PostDetect):
    def __init__(self, controller, delay, duration):
        super().__init__(controller, "DetectAcceleration", delay, duration)
        th, dur = controller.config_manager.get_detection_threshold_and_dur('acceleration')
        self.XY_Smooth_window_size, self.smooth_window_size = controller.config_manager.get_detection_smooth('acceleration')
        self.dur_time = dur
        self.th = th
        self.scale = controller.config_manager.get_scale()
        self.direction_over = controller.config_manager.get_acceleration_direction_over()

        self.last_x = None
        self.last_y = None
        self.last_time = None
        self.last_speed = None
        self.first_over_th_time = None
        self.use_close_loop = (controller.config_manager.get_close_loop_method() == 'Acceleration')
        self.xy_buffer = []
        self.acc_buffer = []
        print(f'scale: {self.scale}')

    def clear_params(self):
        self.last_x = None
        self.last_y = None
        self.last_time = None
        self.last_speed = None
        self.first_over_th_time = None
        self.xy_buffer = []
        self.acc_buffer = []

    def get_res(self, input_data):
        input_data = input_data[1][0]
        current_time, x, y = input_data[0], input_data[1], input_data[2]
        if self.XY_Smooth_window_size > 0:
            self.xy_buffer.append([x, y])
            if len(self.xy_buffer) > self.XY_Smooth_window_size:
                self.xy_buffer.pop(0)
            x, y = np.nanmedian(np.array(self.xy_buffer), 0)
        if np.isnan(x) or np.isnan(y) or self.last_x is None or self.last_y is None:
            self.last_x, self.last_y, self.last_time = x, y, current_time
            return [[False, False, np.nan, np.nan]]
        speed = self.scale * np.sqrt((x - self.last_x) * (x - self.last_x) + (y - self.last_y) * (y - self.last_y))
        speed /= (current_time - self.last_time)
        if self.last_speed is None:
            self.last_x, self.last_y, self.last_time, self.last_speed = x, y, current_time, speed
            return [[False, False, np.nan, np.nan]]
        try:
            acceleration = (speed - self.last_speed) / (current_time - self.last_time)
            if self.smooth_window_size > 0:
                self.acc_buffer.append(acceleration)
                if len(self.acc_buffer) > self.smooth_window_size:
                    self.acc_buffer.pop(0)
                acceleration = np.nanmedian(self.acc_buffer)

            if self.direction_over:
                over_th = acceleration > self.th
            else:
                over_th = acceleration <= self.th

            res = False
            if over_th:
                if self.first_over_th_time is None:
                    self.first_over_th_time = current_time
                if current_time - self.first_over_th_time >= self.dur_time:
                    res = True
            else:
                self.first_over_th_time = None

            if self.use_close_loop:
                self.close_loop_control(res, current_time)

            self.last_x, self.last_y, self.last_time, self.last_speed = x, y, current_time, speed
            return [[res, over_th, speed, acceleration]]
        except Exception:
            return [[False, False, np.nan, np.nan]]


from client_host.Custom import input_data_type, get_res_frame, get_res_xy, get_res_dlc, Custom_name


class DetectCustom(PostDetect):
    def __init__(self, controller, delay, duration, dlc_use_index=None):
        super().__init__(controller, "DetectCustom", delay, duration)
        if dlc_use_index is None:
            dlc_use_index = []
        self.scale = controller.config_manager.get_scale()
        self.area_type, self.area_points = controller.config_manager.get_region_of_interest_area()

        self.use_close_loop = (controller.config_manager.get_close_loop_method() == Custom_name)
        self.dlc_use_index = dlc_use_index

    def get_res(self, input_data):
        if input_data_type == 'frame':
            current_time, input_data = input_data[0], input_data[1]
            res = get_res_frame(input_data, current_time, self.scale, self.area_type, self.area_points)
        elif input_data_type == 'xy':
            input_data = input_data[1][0]
            current_time, x, y = input_data[0], input_data[1], input_data[2]
            res = get_res_xy(x, y, current_time, self.scale, self.area_type, self.area_points)
        else:  # input_data_type == 'dlc-live key points'
            current_time = input_data[1][0][0]
            point_list = input_data[1][0][3:]
            point_list = np.array(point_list).reshape(-1, 3)
            point_list = point_list[self.dlc_use_index]
            res = get_res_dlc(point_list, current_time, self.scale, self.area_type, self.area_points)

        if self.use_close_loop:
            self.close_loop_control(res, current_time)
        return [[res]]
