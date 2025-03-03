from datetime import datetime

from client_host.Camera import RpiCamera
from client_host.Custom import input_data_type
from client_host.TrackModel import DLCLiveModel, TrackLiveModel
from client_host.DataBuffer import DataBuffer
from client_host.GUI.ConfigManager import ConfigManager
from client_host.PlayBack import PlayBack
from client_host.Utils import *
from client_host.PostDetect import DetectPosition, DetectFreezing, DetectSpeed, DetectAcceleration, DetectCustom
from client_host.Recorder import Recorder

PASS = "pass"
POSITION = "position"
FREEZING = "freezing"
SPEED = "speed"


class Controller(object):

    def __init__(self, config_manager: ConfigManager, main_gui):
        self.config_manager = config_manager
        self.main_gui = main_gui

        self.rpi_camera = None

        self.dlc_live = None
        self.track_live = None

        self.freezing_detector = None
        self.speed_detector = None
        self.acceleration_detector = None
        self.position_detector = None
        self.custom_detector = None

        self.track_buffer = None
        self.position_detector_buffer = None
        self.freezing_detector_buffer = None
        self.speed_detector_buffer = None
        self.acceleration_detector_buffer = None
        self.custom_detector_buffer = None

        self.recording_label = False

        self.save_dir = ''
        self.trial_name = ''

    def camera_preview(self):
        if self.rpi_camera is None:
            raise Exception("Init Camera first")
        self.prepare()
        self.rpi_camera.camera_preview()

    def camera_stop_preview(self):
        self.cancel_prepare()
        self.rpi_camera.camera_stop_preview()

    def prepare(self):
        self.dlc_live = None
        self.track_live = None
        self.freezing_detector = None
        self.speed_detector = None
        self.acceleration_detector = None
        self.position_detector = None
        self.custom_detector = None

        detection_config = self.config_manager.get_realtime_detection_config()
        settings_config = self.config_manager.get_settings_config()
        background_photo = self.config_manager.get_background_image()
        fps = int(self.config_manager.get_settings_config()['Camera']['framerate'])
        area_type, area_points = self.config_manager.get_region_of_interest_area()
        duration, delay, interval = self.config_manager.get_settings_close_loop_parameters()

        if detection_config['Custom Method']:
            if input_data_type != 'frame' and input_data_type != 'xy' and input_data_type != 'dlc-live key points':
                raise Exception("Unsupported input data type in Custom: {}".format(input_data_type))
            if input_data_type == 'dlc-live key points' and detection_config['Tracking Method'] and \
                settings_config['Tracking']['method'] != 'DLC_live':
                raise Exception("Custom detection: When selecting DLC-Live key points, DLC-Live must be chosen.")

        self.rpi_camera.set_ttl_params(duration, interval)
        if detection_config['Tracking Method']:
            if settings_config['Tracking']['method'] == 'DLC_live':
                model_path = settings_config['Tracking']['DLC_live_path']
                key_points = settings_config['Tracking']['key_points']
                self.dlc_live = DLCLiveModel(self, model_path, background_photo, area_type, area_points, key_points)
            else:
                self.track_live = TrackLiveModel(self, background_photo, area_type, area_points)
        if detection_config['Freezing Method']:
            self.freezing_detector = DetectFreezing(self, fps, delay, duration)
        if detection_config['Speed Method']:
            self.speed_detector = DetectSpeed(self, fps, delay, duration)
        if detection_config['Acceleration Method']:
            self.acceleration_detector = DetectAcceleration(self, delay, duration)
        if detection_config['Position Method']:
            self.position_detector = DetectPosition(self, delay, duration)
        if detection_config['Custom Method']:
            if input_data_type == 'dlc-live key points' and self.dlc_live is not None:
                self.custom_detector = DetectCustom(self, delay, duration, self.dlc_live.use_index)
            else:
                self.custom_detector = DetectCustom(self, delay, duration)

    def cancel_prepare(self):
        detectors = {
            'dlc_live': self.dlc_live,
            'track_live': self.track_live,
            'freezing_detector': self.freezing_detector,
            'speed_detector': self.speed_detector,
            'acceleration_detector': self.acceleration_detector,
            'position_detector': self.position_detector,
            'custom_detector': self.custom_detector,
        }

        for name, detector in detectors.items():
            if detector is not None:
                detector.close()
                setattr(self, name, None)

    def camera_capture(self):
        if self.rpi_camera is None:
            raise Exception("Init Camera first")
        else:
            photo = self.rpi_camera.capture_photo()
            if photo is None:
                raise Exception("Error in Capture Photo")
            cv2.imshow(f'photo', photo)
            cv2.waitKey(1)
            return photo

    def init_rpiCamera(self, rpi_address, rpi_port, pc_address, pc_port, resolution_width, resolution_height,
                       framerate):
        try:
            self.rpi_camera = RpiCamera(self, rpi_address, pc_address, rpi_port, pc_port,
                                        resolution_width, resolution_height, framerate)
        except Exception as e:
            self.rpi_camera = None
            raise e

    def close_rpiCamera(self):
        if self.rpi_camera is not None:
            self.rpi_camera.close()
            self.rpi_camera = None

    def start_record(self):
        cv2.destroyAllWindows()

        self.save_dir, self.trial_name, record_time = self.config_manager.get_record_parameters()

        self.trial_name = self.trial_name + datetime.now().strftime("_%Y-%m-%d_%H-%M-%S")

        frame_buffer = DataBuffer("frame buffer")

        if self.dlc_live is not None:
            self.track_buffer = DataBuffer("dlc buffer")
            self.dlc_live.start_record(frame_buffer, self.track_buffer)
        elif self.track_live is not None:
            self.track_buffer = DataBuffer("track buffer")
            self.track_live.start_record(frame_buffer, self.track_buffer)

        if self.position_detector is not None:
            self.position_detector_buffer = DataBuffer('position buffer')
            self.position_detector.start_record(self.track_buffer, self.position_detector_buffer)
        if self.freezing_detector is not None:
            self.freezing_detector_buffer = DataBuffer('freezing buffer')
            self.freezing_detector.start_record(frame_buffer, self.freezing_detector_buffer)
        if self.speed_detector is not None:
            self.speed_detector_buffer = DataBuffer('speed buffer')
            self.speed_detector.start_record(self.track_buffer, self.speed_detector_buffer)
        if self.acceleration_detector is not None:
            self.acceleration_detector_buffer = DataBuffer('acceleration buffer')
            self.acceleration_detector.start_record(self.track_buffer, self.acceleration_detector_buffer)
        if self.custom_detector is not None:
            self.custom_detector_buffer = DataBuffer('custom buffer')
            if input_data_type == 'frame':
                self.custom_detector.start_record(frame_buffer, self.custom_detector_buffer)
            else:
                self.custom_detector.start_record(self.track_buffer, self.custom_detector_buffer)

        playback = PlayBack(self, frame_buffer)
        playback.start()

        recorder = Recorder(self, frame_buffer, self.track_buffer, self.save_dir, self.trial_name,
                            fps=self.rpi_camera.get_framerate(), frame_width=self.rpi_camera.get_frame_width(),
                            frame_height=self.rpi_camera.get_frame_height())
        if self.dlc_live is not None:
            recorder.set_dlc_joint_names(self.dlc_live.all_joints_names)

        recorder.start()

        self.rpi_camera.start_record(record_time, frame_buffer)

        self.recording_label = True

    def record_finish(self):
        if self.recording_label:
            self.main_gui.record_gui.func_stop_button()

    def stop_record(self):
        self.recording_label = False
        self.track_buffer = None
        self.position_detector_buffer = None
        self.freezing_detector_buffer = None
        self.speed_detector_buffer = None
        self.acceleration_detector_buffer = None
        self.custom_detector_buffer = None
        self.rpi_camera.stop_record()
