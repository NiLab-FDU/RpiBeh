import threading

import numpy as np

from client_host.Utils import get_largest_component_and_center, point_in_area

if 1:
    from client_host.DataBuffer import DataBuffer


class PostDetect(object):
    def __init__(self, controller, name):
        self.use_dlc = False
        self.controller = controller
        self.process_name = name
        self.last_res = False

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
        pass

    def close(self):
        pass


class DetectPosition(PostDetect):
    def __init__(self, controller, delay):
        super().__init__(controller, "DetectPosition")
        area_type, area_points = controller.config_manager.get_settings_position_parameters()
        self.area_type = area_type
        self.area_points = area_points
        self.delay = delay
        self.first_over_th_time = None
        self.gpio_state = False
        self.use_close_loop = (controller.config_manager.get_close_loop_method() == 'Position')

    def get_res(self, input_data):
        input_data = input_data[1][0]
        current_time, x, y = input_data[0], input_data[1], input_data[2]
        if np.isnan(x) or np.isnan(y):
            return [[False]]
        try:
            res = point_in_area(self.area_type, self.area_points, x, y)
            if self.use_close_loop:
                if res:
                    if self.first_over_th_time is None:
                        self.first_over_th_time = current_time
                    if self.first_over_th_time is not None and (not self.gpio_state) \
                            and current_time - self.first_over_th_time >= self.delay:
                        self.controller.rpi_camera.gpio_start()
                        self.gpio_state = True
                else:
                    self.first_over_th_time = None
                    if self.gpio_state:
                        self.controller.rpi_camera.gpio_stop()
                        self.gpio_state = False
            return [[res]]
        except Exception:
            return [[False]]

    def clear_params(self):
        self.first_over_th_time = None
        self.gpio_state = False


class DetectFreezing(PostDetect):

    def __init__(self, controller, fps, delay):
        super().__init__(controller, "DetectFreezing")
        th, dur = controller.config_manager.get_detection_threshold_and_dur('freezing')
        self.area_type, self.area_points = controller.config_manager.get_region_of_interest_area()
        self.dur_time = dur
        self.threshold = th
        self.fps = fps
        self.delay = delay
        self.over_th_frame_num = max(int(self.dur_time * self.fps), 1)

        self.last_frame = None
        self.count_over_frame_num = 0
        self.first_over_th_time = None
        self.gpio_state = False
        self.use_close_loop = (controller.config_manager.get_close_loop_method() == 'Freezing')

        print(f"DetectFreezing Params\n"
              f"threshold: {self.threshold}\n"
              f"fps: {self.fps}\n"
              f"dur time: {self.dur_time}\n"
              f"over th frame num: {self.over_th_frame_num}")

    def clear_params(self):
        self.last_frame = None
        self.count_over_frame_num = 0
        self.first_over_th_time = None
        self.gpio_state = False

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
                if over_th and not self.gpio_state and self.first_over_th_time is not None and current_time - self.first_over_th_time >= self.delay:
                    self.controller.rpi_camera.gpio_start()
                    self.gpio_state = True
                if self.gpio_state and not over_th:
                    self.controller.rpi_camera.gpio_stop()
                    self.gpio_state = False
                if not res:
                    self.first_over_th_time = None

            self.last_frame = input_data
            return [[res, over_th, area_sum]]
        except Exception:
            self.last_frame = input_data
            return [[False, False, np.nan]]

    def get_params(self):
        return [self.threshold, self.fps, self.over_th_frame_num]


class DetectSpeed(PostDetect):
    def __init__(self, controller, fps, delay):
        super().__init__(controller, "DetectSpeed")
        th, dur = controller.config_manager.get_detection_threshold_and_dur('speed')
        self.dur_time = dur
        self.th = th
        self.delay = delay
        self.scale = controller.config_manager.get_scale()
        self.avg_buffer_window_size = int(fps*0.5)
        self.direction_over = controller.config_manager.get_speed_direction_over()

        self.last_x = None
        self.last_y = None
        self.last_time = None
        self.first_over_th_time = None
        self.speed_buffer = []

        self.gpio_state = False
        self.use_close_loop = (controller.config_manager.get_close_loop_method() == 'Speed')
        print(f"DetectSpeed Params:\n"
              f"threshold: {self.th}")

    def clear_params(self):
        self.last_x = None
        self.last_y = None
        self.last_time = None
        self.first_over_th_time = None
        self.gpio_state = False

    def get_res(self, input_data):
        input_data = input_data[1][0]
        current_time, x, y = input_data[0], input_data[1], input_data[2]
        if np.isnan(x) or np.isnan(y):
            return [[False, False, np.nan]]
        if self.last_x is None or self.last_y is None:
            self.last_x, self.last_y, self.last_time = x, y, current_time
            return [[False, False, np.nan]]
        try:
            speed = self.scale * np.sqrt((x - self.last_x) * (x - self.last_x) + (y - self.last_y) * (y - self.last_y))
            speed /= (current_time - self.last_time)
            self.speed_buffer.append(speed)
            if len(self.speed_buffer) > self.avg_buffer_window_size:
                self.speed_buffer.pop(0)  # 保持窗口大小不超过设定值
            speed = np.mean(self.speed_buffer)  # 均值滤波后的速度
            if self.direction_over:
                over_th = speed > self.th
            else:
                over_th = speed <= self.th
            res = False
            if self.dur_time == 0:
                res = over_th
            elif over_th:
                if self.first_over_th_time is None:
                    self.first_over_th_time = current_time
                elif current_time - self.first_over_th_time >= self.dur_time:
                    res = True
            else:
                self.first_over_th_time = None

            if self.use_close_loop:
                if over_th and (not self.gpio_state) and self.first_over_th_time is not None and current_time - self.first_over_th_time >= self.delay:
                    self.controller.rpi_camera.gpio_start()
                    self.gpio_state = True
                if self.gpio_state and not over_th:
                    self.controller.rpi_camera.gpio_stop()
                    self.gpio_state = False

            self.last_x, self.last_y, self.last_time = x, y, current_time
            return [[res, over_th, speed]]
        except Exception:
            return [[False, False, np.nan]]

    def get_params(self):
        return [self.th]


class DetectAcceleration(PostDetect):
    def __init__(self, controller, delay):
        super().__init__(controller, "DetectAcceleration")
        th, dur = controller.config_manager.get_detection_threshold_and_dur('acceleration')
        self.dur_time = dur
        self.th = th
        self.delay = delay
        self.scale = controller.config_manager.get_scale()
        self.direction_over = controller.config_manager.get_acceleration_direction_over()

        self.last_x = None
        self.last_y = None
        self.last_time = None
        self.last_speed = None
        self.first_over_th_time = None

        self.gpio_state = False
        self.use_close_loop = (controller.config_manager.get_close_loop_method() == 'Acceleration')

    def clear_params(self):
        self.last_x = None
        self.last_y = None
        self.last_time = None
        self.last_speed = None
        self.first_over_th_time = None
        self.gpio_state = False

    def get_res(self, input_data):
        input_data = input_data[1][0]
        current_time, x, y = input_data[0], input_data[1], input_data[2]
        if np.isnan(x) or np.isnan(y):
            return [[False, False, np.nan, np.nan]]
        if self.last_x is None or self.last_y is None or self.last_time is None:
            self.last_x, self.last_y, self.last_time = x, y, current_time
            return [[False, False, np.nan, np.nan]]
        try:
            current_speed = self.scale * np.sqrt((x - self.last_x) ** 2 + (y - self.last_y) ** 2)
            current_speed /= (current_time - self.last_time)

            if self.last_speed is None:
                self.last_x, self.last_y, self.last_time, self.last_speed = x, y, current_time, current_speed
                return [[False, False, current_speed, np.nan]]

            acceleration = (current_speed - self.last_speed) / (current_time - self.last_time)

            if self.direction_over:
                over_th = acceleration > self.th
            else:
                over_th = acceleration <= self.th

            res = False
            if self.dur_time == 0:
                res = over_th
            elif over_th:
                if self.first_over_th_time is None:
                    self.first_over_th_time = current_time
                elif current_time - self.first_over_th_time >= self.dur_time:
                    res = True
            else:
                self.first_over_th_time = None

            if self.use_close_loop:
                if over_th and (not self.gpio_state) and self.first_over_th_time is not None \
                        and current_time - self.first_over_th_time >= self.delay:
                    self.controller.rpi_camera.gpio_start()
                    self.gpio_state = True
                if self.gpio_state and not over_th:
                    self.controller.rpi_camera.gpio_stop()
                    self.gpio_state = False

            self.last_x, self.last_y, self.last_time, self.last_speed = x, y, current_time, current_speed
            return [[res, over_th, current_speed, acceleration]]
        except Exception:
            return [[False, False, np.nan, np.nan]]

