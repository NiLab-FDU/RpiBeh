import threading
import numpy as np
import cv2

from client_host.Custom import Custom_name
from client_host.Utils import cv2_fill


class PlayBack:
    def __init__(self, controller, frame_buffer):
        self.controller = controller
        self.detector_type = controller.config_manager.get_close_loop_method()
        if self.detector_type == 'Freezing':
            detector_buffer = controller.freezing_detector_buffer
        elif self.detector_type == 'Speed':
            detector_buffer = controller.speed_detector_buffer
        elif self.detector_type == 'Acceleration':
            detector_buffer = controller.acceleration_detector_buffer
        elif self.detector_type == 'Position':
            detector_buffer = controller.position_detector_buffer
            self.area_type, self.area_points = controller.config_manager.get_settings_position_parameters()
        elif self.detector_type == Custom_name:
            detector_buffer = controller.custom_detector_buffer
        else:
            detector_buffer = None

        self.track_buffer_reader_index = -1
        self.detector_buffer_reader_index = -1

        self.frame_buffer = frame_buffer
        self.track_buffer = controller.track_buffer
        self.detector_buffer = detector_buffer

        self.frame_buffer_reader_index = frame_buffer.register_reader()
        if self.track_buffer is not None:
            self.track_buffer_reader_index = self.track_buffer.register_reader()
            if self.detector_buffer is not None:
                self.detector_buffer_reader_index = self.detector_buffer.register_reader()

        self.use_detector = detector_buffer is not None
        self.use_track = self.track_buffer is not None
        self.use_dlc = controller.dlc_live is not None
        self.dlc_use_index = []
        if self.use_dlc:
            self.dlc_use_index = controller.dlc_live.use_index

        self.radius = 3

    def start(self):
        print("play back start")
        thread = threading.Thread(target=self.play)
        thread.start()

    def get_frame_track_detect_res(self):
        track_res = None
        detect_res = None
        if not self.use_track:
            if self.use_detector:
                detect_index, detect_res = self.detector_buffer.get_last_data(self.detector_buffer_reader_index)
                if detect_index is None:
                    return None, 'break', None
                if detect_res is None:
                    return None, 'continue', None
                frame_index, detect_res = detect_res[0], detect_res[1]
                frame_index, frame = self.frame_buffer.get_data_by_index(self.frame_buffer_reader_index, frame_index)
            else:
                index, frame = self.frame_buffer.get_data(self.frame_buffer_reader_index)
                if index is None:
                    return None, 'break', None
        else:
            if self.use_detector:
                detect_index, detect_res = self.detector_buffer.get_last_data(self.detector_buffer_reader_index)
                if detect_index is None:
                    return None, 'break', None
                if detect_res is None:
                    return None, 'continue', None
                track_index, detect_res = detect_res[0], detect_res[1]
                track_index, track_res = self.track_buffer.get_data_by_index(self.track_buffer_reader_index,
                                                                             track_index)
            else:
                track_index, track_res = self.track_buffer.get_last_data(self.track_buffer_reader_index)

            if track_index is None:
                return None, 'break', None
            if track_res is None:
                return None, 'continue', None

            frame_index, track_res = track_res[0], track_res[1]
            frame_index, frame = self.frame_buffer.get_data_by_index(self.frame_buffer_reader_index, frame_index)

        frame = frame[1]
        return frame, track_res, detect_res

    def frame_improve(self, frame, track_res, detect_res):
        if self.use_track:
            if self.use_dlc:
                out = track_res[0]
                x, y = int(out[1]), int(out[2])
                if not np.isnan(x):
                    frame = cv2.circle(frame, (x, y), self.radius, (0, 255, 0), thickness=-1)
                point_list = np.array(out[3:]).reshape(-1, 3)
                point_list = point_list[self.dlc_use_index]
                for point in point_list:
                    x, y = int(point[0]), int(point[1])
                    if not np.isnan(x):
                        frame = cv2.circle(frame, (x, y), 1, (255, 0, 0), thickness=-1)
            else:
                out, _, _, largest_contour = track_res
                _, x, y = out
                if largest_contour is not None:
                    cv2.drawContours(frame, [largest_contour], -1, (255, 0, 0), 2)
                    frame = cv2.circle(frame, (x, y), self.radius, (0, 255, 0), thickness=-1)
        if self.detector_type == 'Position':
            mask = cv2_fill(np.zeros_like(frame), self.area_type, self.area_points, (255, 255, 255))
            shadow = cv2_fill(np.zeros_like(frame), self.area_type, self.area_points,(0, 255, 0))
            frame_with_shadow = cv2.addWeighted(src1=frame, alpha=1, src2=shadow, beta=0.2, gamma=0)
            frame[mask != 0] = frame_with_shadow[mask != 0]
        if self.use_detector:
            center = (frame.shape[0] - 20, frame.shape[1] - 20)
            radius = 10
            if detect_res[0][0]:
                color = (0, 255, 0)
            else:
                color = (128, 128, 128)
            cv2.circle(frame, center, radius, color, -1)
        return frame

    def play(self):
        cv2.destroyAllWindows()
        while True:
            frame, track_res, detect_res = self.get_frame_track_detect_res()
            if frame is None:
                if track_res == 'break':
                    break
                if track_res == 'continue':
                    continue

            frame = self.frame_improve(frame, track_res, detect_res)

            if frame is not None:
                cv2.imshow(f'Frame', frame)
                cv2.waitKey(1)
