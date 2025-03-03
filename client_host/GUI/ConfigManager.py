import json
import os

import cv2
import numpy as np

from client_host.GUI.SettingsGUI import SettingsGUI


class ConfigManager:
    def __init__(self, main_gui):
        self.main_gui = main_gui
        self.settings_config = None
        self.rpi_camera_config = None
        self.realtime_detection_config = None
        self.close_loop_config = None
        self.analysis_config = None
        self.record_config = None
        self.image = None

        self.init_settings_config()
        self.init_rpi_camera_config()
        self.init_realtime_detection_config()
        self.init_close_loop_config()
        self.init_analysis_config()
        self.init_record_config()

    def update_config_manager(self):
        config = self.main_gui.get_config()
        self.rpi_camera_config = config['RpiCamera']
        self.realtime_detection_config = config['RealtimeDetection']
        self.close_loop_config = config['CloseLoop']
        self.analysis_config = config['Analysis']
        self.record_config = config['Record']

    def check_position_detection_setting_exist(self):
        if self.settings_config is not None and \
                "Position" in self.settings_config and \
                "area_type" in self.settings_config["Position"]:
            return True
        SettingsGUI(self.main_gui.root, self, 'Position')
        return (self.settings_config is not None and
                "Position" in self.settings_config and
                "area_type" in self.settings_config["Position"])

    def check_selected_area_analysis_setting_exist(self):
        if (self.settings_config is not None and
                "Selected area analysis" in self.settings_config and
                "area_types" in self.settings_config["Selected area analysis"]):
            return True
        SettingsGUI(self.main_gui.root, self, 'Selected area analysis')
        return (self.settings_config is not None and
                "Selected area analysis" in self.settings_config and
                "area_types" in self.settings_config["Selected area analysis"])

    def init_settings_config(self):
        if self.settings_config is None:
            self.settings_config = {}
            config_keys = ['Camera', 'Region of interest', 'Tracking', 'Detection', 'Position', 'Close Loop',
                           'Selected area analysis']
            for key in config_keys:
                self.settings_config[key] = {}
            self.settings_config['Camera']['framerate'] = '15'
            self.settings_config['Camera']['image_size'] = '640*640'
            self.settings_config['Tracking']['method'] = 'BG_subtraction'
            self.settings_config['Detection']['freezing_threshold'] = '0.007'
            self.settings_config['Detection']['freezing_duration'] = '0.5s'
            self.settings_config['Detection']['speed_threshold'] = '0.007'
            self.settings_config['Detection']['speed_duration'] = '0.5s'
            self.settings_config['Detection']['speed_direction'] = 'over'
            self.settings_config['Detection']['speed_XY_Smooth'] = '5'
            self.settings_config['Detection']['speed_Smooth'] = '5'
            self.settings_config['Detection']['acceleration_threshold'] = '0.007'
            self.settings_config['Detection']['acceleration_duration'] = '0.5s'
            self.settings_config['Detection']['acceleration_direction'] = 'over'
            self.settings_config['Detection']['acceleration_XY_Smooth'] = '5'
            self.settings_config['Detection']['acceleration_Smooth'] = '5'
            self.settings_config['Close Loop']['duration'] = '0.2'
            self.settings_config['Close Loop']['delay'] = '2'
            self.settings_config['Close Loop']['interval'] = '0'

    def init_rpi_camera_config(self):
        if self.rpi_camera_config is None:
            self.rpi_camera_config = {}
            config_keys = ['rpi_address', 'rpi_port', 'pc_address', 'pc_port']
            for key in config_keys:
                self.rpi_camera_config[key] = ''

    def get_camera_config_setting(self):
        self.init_settings_config()
        resolution_width, resolution_height = self.settings_config['Camera']['image_size'].split("*")
        framerate = self.settings_config['Camera']['framerate']
        return int(resolution_width), int(resolution_height), int(framerate)

    def init_realtime_detection_config(self):
        if self.realtime_detection_config is None:
            self.realtime_detection_config = {}
            config_keys = ['Tracking Method', 'Freezing Method', 'Speed Method', 'Acceleration Method',
                           'Position Method', 'Custom Method']
            for key in config_keys:
                self.realtime_detection_config[key] = False

    def init_close_loop_config(self):
        if self.close_loop_config is None:
            self.close_loop_config = {'Close Loop Method': 'None'}

    def init_analysis_config(self):
        if self.analysis_config is None:
            self.analysis_config = {}
            config_keys = ['Heat Map', 'Trajectory Map', 'Freezing Analysis', 'Selected Area Analysis']
            for key in config_keys:
                self.analysis_config[key] = False

    def init_record_config(self):
        if self.record_config is None:
            self.record_config = {}
            self.record_config = {'Dir': '', 'Trial': '', 'Time': ''}

    def get_background_image(self):
        return self.image

    def get_close_loop_method(self):
        return self.close_loop_config['Close Loop Method']

    def get_scale(self):        # cm/pixel
        start_x, start_y, stop_x, stop_y = self.settings_config['Region of interest']['line']
        pixel_distance = np.sqrt((stop_x - start_x) ** 2 + (stop_y - start_y) ** 2)
        return float(self.settings_config['Region of interest']['real distance']) / pixel_distance

    def get_detection_threshold_and_dur(self, detection_name):
        config = self.settings_config['Detection']
        return float(config[detection_name+'_threshold']), float(config[detection_name+'_duration'].split('s')[0])

    def get_detection_smooth(self, detection_name):
        config = self.settings_config['Detection']
        return int(config[detection_name+'_XY_Smooth']), int(config[detection_name+'_Smooth'])

    def get_settings_position_parameters(self):
        config = self.settings_config['Position']
        return config['area_type'], np.array(config['area_points'])

    def get_settings_close_loop_parameters(self):
        config = self.settings_config['Close Loop']
        return float(config['duration']), float(config['delay']), float(config['interval'])

    def get_speed_direction_over(self):
        return self.settings_config['Detection']['speed_direction'] == 'over'

    def get_acceleration_direction_over(self):
        return self.settings_config['Detection']['acceleration_direction'] == 'over'

    def get_settings_selected_area_analysis(self):
        config = self.settings_config['Selected area analysis']
        return config['area_types'], config['area_points']

    def get_region_of_interest_area(self):
        config = self.settings_config['Region of interest']
        return config['area_type'], np.array(config['area_points'])

    def get_settings_config(self):
        return self.settings_config

    def get_rpi_camera_config(self):
        return self.rpi_camera_config

    def get_realtime_detection_config(self):
        return self.realtime_detection_config

    def get_close_loop_config(self):
        return self.close_loop_config

    def get_analysis_config(self):
        return self.analysis_config

    def get_record_config(self):
        return self.record_config

    def get_record_parameters(self):
        dir_path = self.record_config['Dir']
        trial_name = self.record_config['Trial']
        record_time = float(self.record_config['Time'])
        return dir_path, trial_name, record_time

    def set_image(self, image):
        self.image = image

    def set_settings_config(self, config):
        self.settings_config = config

    def save_config(self, filepath=None):
        config = self.main_gui.get_config()
        if filepath is None:
            filepath = 'last_config.json'
        if self.image is not None:
            image_output_path = os.path.join(os.path.dirname(filepath), 'background_image.png')
            cv2.imwrite(image_output_path, self.image)
            config['BackgroundImagePath'] = image_output_path
        with open(filepath, "w") as json_file:
            json.dump(config, json_file, indent=4)

    def load_config(self, filepath=None):
        if filepath is None:
            filepath = 'last_config.json'
        if os.path.exists(filepath):
            with open(filepath, "r") as json_file:
                config = json.load(json_file)
        else:
            config = {}

        if 'BackgroundImagePath' in config and os.path.exists(config['BackgroundImagePath']):
            try:
                image = cv2.imread(config['BackgroundImagePath'])
                self.image = image
            except Exception as e:
                self.image = None
        else:
            self.image = None

        if 'Settings' in config:
            self.settings_config = config['Settings']
        else:
            self.init_settings_config()

        if 'RpiCamera' in config:
            self.rpi_camera_config = config['RpiCamera']
        else:
            self.init_rpi_camera_config()

        if 'RealtimeDetection' in config:
            self.realtime_detection_config = config['RealtimeDetection']
        else:
            self.init_realtime_detection_config()

        if 'CloseLoop' in config:
            self.close_loop_config = config['CloseLoop']
        else:
            self.init_close_loop_config()

        if 'Analysis' in config:
            self.analysis_config = config['Analysis']
        else:
            self.init_analysis_config()

        if 'Record' in config:
            self.record_config = config['Record']
        else:
            self.init_record_config()

        return config
