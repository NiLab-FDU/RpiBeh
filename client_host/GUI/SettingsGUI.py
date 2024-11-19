import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from PIL import Image, ImageTk

import yaml


class SettingsGUI:
    def __init__(self, root, config_manager, setting_name):
        self.config_manager = config_manager
        self.image = self.config_manager.get_background_image()

        self.setting_window = tk.Toplevel(root)
        self.setting_window.title("Settings")
        self.setting_window.geometry("940x740")
        self.setting_window.protocol("WM_DELETE_WINDOW", self.on_close)

        left_frame = ttk.Frame(self.setting_window, width=200, height=740, relief=tk.SUNKEN)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = ttk.Frame(self.setting_window, width=740, height=740, relief=tk.SUNKEN)
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.style = ttk.Style()
        self.style.configure("Selected.TButton", background="black")
        self.style.configure("TButton", background="white")

        settings_options = [
            "Camera", "Region of interest", "Tracking", "Detection", "Position",
            "Close Loop", "Selected area analysis"
        ]

        self.setting_button_dist = {}
        for setting in settings_options:
            button = ttk.Button(left_frame, text=setting, command=lambda s=setting: self.show_setting(s))
            button.pack(fill=tk.X, padx=10, pady=5)
            self.setting_button_dist[setting] = button

        self.config = self.config_manager.get_settings_config()
        self.current_frame = None
        self.current_page = None
        self.current_setting = None
        self.show_setting(setting_name)

        self.setting_window.grab_set()
        self.setting_window.transient(root)
        self.setting_window.wait_window()

    def on_close(self):
        if self.current_page is not None:
            if not self.current_page.save_config():
                return
        self.config_manager.set_settings_config(self.config)
        self.setting_window.destroy()

    def reset_button_styles(self):
        for button in self.setting_button_dist.values():
            button.config(style="TButton")

    def show_setting(self, setting_name):
        if self.current_setting is not None and self.current_setting == setting_name:
            return
        if self.current_page is not None:
            if not self.current_page.save_config():
                return

        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_setting = setting_name
        self.reset_button_styles()
        self.setting_button_dist[setting_name].config(style="Selected.TButton")
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        self.build_setting_page(setting_name)

    def build_setting_page(self, setting_name):
        font_bold = ("Arial", 12, "bold")
        ttk.Label(self.right_frame, text=setting_name + " Settings Page", font=font_bold).pack(pady=10)

        self.current_frame = ttk.Frame(self.right_frame)
        self.current_frame.pack(pady=10)

        if setting_name == 'Camera':
            self.current_page = CameraSettingPage(self.current_frame, self.config)
        elif setting_name == 'Region of interest':
            self.current_page = RegionOfInterestSettingPage(self.current_frame, self.config, self.image)
        elif setting_name == 'Tracking':
            self.current_page = TrackingSettingPage(self.current_frame, self.config)
        elif setting_name == 'Detection':
            self.current_page = DetectionSettingPage(self.current_frame, self.config)
        elif setting_name == 'Position':
            self.current_page = PositionSettingPage(self.current_frame, self.config, self.image)
        elif setting_name == 'Close Loop':
            self.current_page = CloseLoopSettingPage(self.current_frame, self.config)
        elif setting_name == 'Selected area analysis':
            self.current_page = SelectedAreaAnalysisSettingPage(self.current_frame, self.config, self.image)


class CameraSettingPage:
    def __init__(self, frame, config):
        self.frame = frame
        self.config = config
        ttk.Label(frame, text="Framerate:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.framerate_var = tk.StringVar()
        self.framerate_combobox = ttk.Combobox(frame, textvariable=self.framerate_var, state="readonly")
        self.framerate_combobox['values'] = ("5", "10", "15")
        self.framerate_combobox.grid(row=0, column=1, padx=10, pady=5)
        if 'framerate' in config['Camera']:
            self.framerate_var.set(config['Camera']['framerate'])
        else:
            self.framerate_combobox.current(2)

        ttk.Label(frame, text="Image size:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.img_size_var = tk.StringVar()
        self.img_size_combobox = ttk.Combobox(frame, textvariable=self.img_size_var, state="readonly")
        self.img_size_combobox['values'] = ('512*512', '640*640')
        self.img_size_combobox.grid(row=1, column=1, padx=10, pady=5)
        if 'image_size' in config['Camera']:
            self.img_size_var.set(config['Camera']['image_size'])
        else:
            self.img_size_combobox.current(1)

        # https://www.zhihu.com/question/595208346
        # Add a hidden button to make the default value visible
        ttk.Button(frame, text="Get Values", command=self.get_selected_values, state="disabled")

    def get_selected_values(self):
        framerate = self.framerate_var.get()
        img_size = self.img_size_var.get()
        print(f"Selected Framerate: {framerate}, Image Size: {img_size}")

    def save_config(self):
        self.config['Camera']['framerate'] = self.framerate_var.get()
        self.config['Camera']['image_size'] = self.img_size_var.get()
        return True


class BasePictureSelectSettingPage:
    def __init__(self, frame, config, image):
        self.config = config
        if image is not None:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(image))
            self.canvas = tk.Canvas(frame, width=self.photo.width(), height=self.photo.height())
            self.canvas.pack(side=tk.LEFT, anchor=tk.CENTER, pady=(0, 0))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        else:
            self.canvas = tk.Canvas(frame, width=640, height=640)
            self.canvas.pack(side=tk.LEFT, anchor=tk.CENTER, pady=(0, 0))
            self.canvas.create_text(320, 320, text="Please capture a background image first",
                                    font=("Arial", 16), fill="black")

        button_frame = ttk.Frame(frame)
        button_frame.pack(side=tk.RIGHT)

        # select area
        ttk.Label(button_frame, text='Select Area').pack()
        ttk.Button(button_frame, text='Rectangle', command=lambda: self.select_shape_select('rectangle')).pack()
        ttk.Button(button_frame, text='Circle', command=lambda: self.select_shape_select('circle')).pack()
        ttk.Button(button_frame, text='Polygon', command=lambda: self.select_shape_select('polygon')).pack()

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.button_frame = button_frame

        # tmp var
        self.start_x = None
        self.start_y = None
        self.mode = None
        self.shape_type = 'rectangle'

        self.area_select = None
        self.polygon_points_select = []

    def init_shape(self, setting_name):
        if 'area_type' not in self.config[setting_name]:
            return

        area_type = self.config[setting_name]['area_type']
        area_points = self.config[setting_name]['area_points']

        if area_type == 'rectangle':
            self.area_select = self.canvas.create_rectangle(area_points, outline='blue')
        elif area_type == 'oval':
            self.area_select = self.canvas.create_oval(area_points, outline='blue')
        elif area_type == 'polygon':
            self.area_select = self.canvas.create_polygon(area_points, outline='blue', fill='', smooth=False)

    def set_area_mode_select(self):
        self.mode = 'area_select'
        if self.area_select:
            self.canvas.delete(self.area_select)
        self.area_select = None
        self.polygon_points_select.clear()

    def select_shape_select(self, shape):
        self.shape_type = shape
        self.set_area_mode_select()

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

        if self.mode == 'scale':
            self.line = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y, fill='red')
        elif self.mode == 'area_select':
            if self.shape_type == 'rectangle':
                self.area_select = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                                outline='blue')
            elif self.shape_type == 'circle':
                self.area_select = self.canvas.create_oval(self.start_x, self.start_y, self.start_x, self.start_y,
                                                           outline='blue')
            elif self.shape_type == 'polygon':
                self.polygon_points_select.append((self.start_x, self.start_y))
                if self.area_select is not None:
                    self.canvas.delete(self.area_select)
                self.area_select = self.canvas.create_polygon(self.polygon_points_select, outline='blue', fill='',
                                                              smooth=False)

    def on_mouse_drag(self, event):
        if self.mode == 'scale' and self.line:
            self.canvas.coords(self.line, self.start_x, self.start_y, event.x, event.y)
        elif self.mode == 'area_select':
            area = self.area_select

            if self.shape_type == 'rectangle' and area:
                self.canvas.coords(area, self.start_x, self.start_y, event.x, event.y)
            elif self.shape_type == 'circle' and area:
                radius = self.calculate_length(self.start_x, self.start_y, event.x, event.y)
                self.canvas.coords(area, self.start_x - radius, self.start_y - radius, self.start_x + radius,
                                   self.start_y + radius)
            elif self.shape_type == 'polygon':
                pass

    def on_button_release(self, event):
        if not (self.mode == 'area_select' and self.shape_type == 'polygon'):
            self.mode = None

    def validate_positive_input(self, new_value):
        if new_value == "":
            return True
        try:
            value = float(new_value)
            if value >= 0:
                return True
        except ValueError:
            return False
        return False

    def calculate_length(self, x1, y1, x2, y2):
        """Calculate the distance between two points."""
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


class PositionSettingPage(BasePictureSelectSettingPage):
    def __init__(self, frame, config, image):
        super().__init__(frame, config, image)
        self.init_shape('Position')

    def save_config(self):
        if self.area_select is not None:
            self.config['Position']['area_type'] = self.canvas.type(self.area_select)
            self.config['Position']['area_points'] = self.canvas.coords(self.area_select)
        else:
            self.config['Position'].pop('area_type', None)
            self.config['Position'].pop('area_points', None)
        return True


class RegionOfInterestSettingPage(BasePictureSelectSettingPage):
    def __init__(self, frame, config, image):
        super().__init__(frame, config, image)
        self.line = None
        self.init_shape('Region of interest')
        # scale
        ttk.Label(self.button_frame, text='Scale').pack(pady=(80, 0))
        ttk.Button(self.button_frame, text="Set Scale", command=self.set_scale_mode).pack()
        ttk.Label(self.button_frame, text='Real Distance (cm)').pack()
        vcmd = (self.button_frame.register(self.validate_positive_input), '%P')
        self.scale_entry = ttk.Entry(self.button_frame, validate='key', validatecommand=vcmd, width=10)
        if 'real distance' in config['Region of interest']:
            self.scale_entry.delete(0, tk.END)
            self.scale_entry.insert(0, config['Region of interest']['real distance'])
        self.scale_entry.pack()

    def set_scale_mode(self):
        self.mode = 'scale'
        if self.line is not None:
            self.canvas.delete(self.line)
            self.line = None

    def save_config(self):
        self.config['Region of interest']['real distance'] = self.scale_entry.get()
        if self.line is not None:
            self.config['Region of interest']['line'] = self.canvas.coords(self.line)
        else:
            self.config['Region of interest'].pop('line', None)
        if self.area_select is not None:
            self.config['Region of interest']['area_type'] = self.canvas.type(self.area_select)
            self.config['Region of interest']['area_points'] = self.canvas.coords(self.area_select)
        else:
            self.config['Region of interest'].pop('area_type', None)
            self.config['Region of interest'].pop('area_points', None)
        return True

    def init_shape(self, setting_name):
        if 'area_type' in self.config[setting_name]:
            area_type = self.config[setting_name]['area_type']
            area_points = self.config[setting_name]['area_points']

            if area_type == 'rectangle':
                self.area_select = self.canvas.create_rectangle(area_points, outline='blue')
            elif area_type == 'oval':
                self.area_select = self.canvas.create_oval(area_points, outline='blue')
            elif area_type == 'polygon':
                self.area_select = self.canvas.create_polygon(area_points, outline='blue', fill='', smooth=False)
        if 'line' in self.config[setting_name]:
            self.line = self.canvas.create_line(self.config[setting_name]['line'], fill='red')


class TrackingSettingPage:
    def __init__(self, frame, config):
        self.config = config

        self.detection_result = None

        ttk.Label(frame, text="Tracking method:").grid(row=0, column=0, padx=2, pady=5, sticky=tk.W)

        self.tracking_method_var = tk.StringVar(value='BG_subtraction')
        self.bg_subtraction_rb = ttk.Radiobutton(frame, text="Background subtraction method",
                                                 variable=self.tracking_method_var, value="BG_subtraction",
                                                 command=self.on_tracking_method_change)
        self.dlc_live_rb = ttk.Radiobutton(frame, text="DLC-live", variable=self.tracking_method_var,
                                           value="DLC_live", command=self.on_tracking_method_change)

        self.bg_subtraction_rb.grid(row=0, column=1, padx=2, pady=5, sticky=tk.W)
        self.dlc_live_rb.grid(row=0, column=2, padx=2, pady=5, sticky=tk.W)

        # DLC-live options (hidden initially)
        self.dlc_live_frame = ttk.Frame(frame)
        self.dlc_live_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W)
        self.dlc_live_frame.grid_remove()

        ttk.Label(self.dlc_live_frame, text="DLC-live path:").grid(row=0, column=0, padx=2, pady=5,
                                                                   sticky=tk.W)
        self.dlc_live_path_var = tk.StringVar()
        self.dlc_live_entry = ttk.Entry(self.dlc_live_frame, textvariable=self.dlc_live_path_var, width=35)
        self.dlc_live_entry.grid(row=0, column=1, padx=2, pady=5, sticky=tk.W)
        self.dlc_live_entry.bind("<KeyRelease>", self.on_path_change)

        self.dlc_live_button = ttk.Button(self.dlc_live_frame, text="Open", command=self.select_dlc_live_path)
        self.dlc_live_button.grid(row=0, column=2, padx=2, pady=5, sticky=tk.W)

        self.detection_button = ttk.Button(self.dlc_live_frame, text="Load", command=self.run_detection)
        self.detection_button.grid(row=1, column=2, padx=2, pady=5, sticky=tk.W)

        self.status_label = ttk.Label(self.dlc_live_frame, text="")
        self.status_label.grid(row=1, column=1, padx=4, pady=5, sticky=tk.E)

        ttk.Label(self.dlc_live_frame, text="Key points used to calculate the center point:"). \
            grid(row=2, column=0, columnspan=3, padx=2, pady=2, sticky=tk.W)

        self.new_keypoints = {}
        self.keypoints_var = {}
        if 'key_points' in self.config['Tracking']:
            key_points = self.config['Tracking']['key_points']
            for key in key_points.keys():
                self.new_keypoints[key] = tk.BooleanVar(value=key_points[key])
                self.keypoints_var[key] = self.new_keypoints[key]
        if 'method' in self.config['Tracking']:
            self.tracking_method_var.set(self.config['Tracking']['method'])
        self.on_tracking_method_change()
        if 'DLC_live_path' in self.config['Tracking']:
            self.dlc_live_path_var.set(self.config['Tracking']['DLC_live_path'])
        if 'detection_result' in self.config['Tracking']:
            if self.config['Tracking']['detection_result'] is not None:
                self.run_detection(self.config['Tracking']['detection_result'])
            else:
                self.status_label.config(text="to be Load")

    def on_path_change(self, event):
        self.status_label.config(text="to be Load")

    def clear_keypoint_checkboxes(self):
        """Remove all existing keypoint checkboxes from the grid."""
        for widget in self.dlc_live_frame.grid_slaves():
            if isinstance(widget, ttk.Checkbutton):
                widget.grid_forget()

    def add_keypoint_checkboxes(self):
        """Add new checkboxes based on the updated keypoints_var dictionary."""
        row_offset = 3
        for idx, (keypoint, var) in enumerate(self.keypoints_var.items()):
            ttk.Checkbutton(self.dlc_live_frame, text=keypoint, variable=var). \
                grid(row=row_offset + idx, column=0, columnspan=3, padx=10, pady=2, sticky=tk.W)

    def run_detection(self, detection_result=None):
        if detection_result is None:
            self.detection_result = self.detection_function()
        else:
            self.detection_result = detection_result

        if self.detection_result is None:
            self.status_label.config(text="to be Load")
        elif self.detection_result:
            self.clear_keypoint_checkboxes()
            self.keypoints_var.update(self.new_keypoints)
            self.add_keypoint_checkboxes()

            self.status_label.config(text="Load Succeed")
        else:
            self.status_label.config(text="Load Failed")

    def detection_function(self):
        filepath = os.path.join(self.dlc_live_entry.get(), 'pose_cfg.yaml')
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
                data = data['all_joints_names']
                self.new_keypoints.update({})
                for keypoint in data:
                    self.new_keypoints[keypoint] = tk.BooleanVar(value=True)
                return True
        except Exception as e:
            return False

    def on_tracking_method_change(self):
        if self.tracking_method_var.get() == "DLC_live":
            self.dlc_live_frame.grid()
        else:
            self.dlc_live_frame.grid_remove()

    def select_dlc_live_path(self):
        folder_path = tk.filedialog.askdirectory()
        if folder_path:
            self.dlc_live_path_var.set(folder_path)
            self.on_path_change(None)

    def save_config(self):
        self.config['Tracking']['method'] = self.tracking_method_var.get()
        self.config['Tracking']['DLC_live_path'] = self.dlc_live_path_var.get()
        self.config['Tracking']['detection_result'] = self.detection_result
        key_points = {}
        for keypoint in self.new_keypoints.keys():
            key_points[keypoint] = self.new_keypoints[keypoint].get()
        self.config['Tracking']['key_points'] = key_points
        if self.config['Tracking']['method'] == 'DLC_live' and \
                len(key_points) > 0 and all(value is False for value in key_points.values()):
            messagebox.showerror("Error", "Need at least one key point.")
            return False
        return True


class DetectionSettingPage:
    def __init__(self, frame, config):
        self.config = config

        ttk.Label(frame, text="Threshold").grid(row=0, column=1)
        ttk.Label(frame, text="Direction").grid(row=0, column=2)
        ttk.Label(frame, text="Duration").grid(row=0, column=3)
        ttk.Label(frame, text="Freezing").grid(row=1, column=0)
        ttk.Label(frame, text="Speed").grid(row=2, column=0)
        ttk.Label(frame, text="Acceleration").grid(row=3, column=0)

        # Freezing threshold and duration
        self.freezing_threshold_var = tk.StringVar()
        if 'freezing_threshold' in config['Detection']:
            self.freezing_threshold_var.set(config['Detection']['freezing_threshold'])
        else:
            self.freezing_threshold_var.set("0.007")
        self.validate_range = frame.register(self.validate_entry)
        self.validate_range_ratio = frame.register(self.validate_entry_ratio)
        freezing_threshold_entry = ttk.Entry(frame, textvariable=self.freezing_threshold_var, validate="key",
                                             validatecommand=(self.validate_range_ratio, '%P'))
        freezing_threshold_entry.grid(row=1, column=1, padx=10, pady=5)

        self.freezing_duration_var = tk.StringVar()
        freezing_duration_combobox = ttk.Combobox(frame, textvariable=self.freezing_duration_var, state="readonly",
                                                  width=10)
        freezing_duration_combobox['values'] = ['0s', '0.2s', '0.5s', '1s', '1.5s', '2s']
        if 'freezing_duration' in config['Detection']:
            self.freezing_duration_var.set(config['Detection']['freezing_duration'])
        else:
            freezing_duration_combobox.set('0.5s')
        freezing_duration_combobox.grid(row=1, column=3, padx=10, pady=5)

        # Speed threshold and duration
        self.speed_threshold_var = tk.StringVar()
        if 'speed_threshold' in config['Detection']:
            self.speed_threshold_var.set(config['Detection']['speed_threshold'])
        else:
            self.speed_threshold_var.set("0.007")
        speed_threshold_entry = ttk.Entry(frame, textvariable=self.speed_threshold_var, validate="key",
                                          validatecommand=(self.validate_range, '%P'))
        speed_threshold_entry.grid(row=2, column=1, padx=10, pady=5)

        self.speed_direction_var = tk.StringVar()
        speed_direction_combobox = ttk.Combobox(frame, textvariable=self.speed_direction_var, state="readonly", width=10)
        speed_direction_combobox['values'] = ['over', 'below']
        if 'speed_direction' in config['Detection']:
            self.speed_direction_var.set(config['Detection']['speed_direction'])
        else:
            speed_direction_combobox.set('over')
        speed_direction_combobox.grid(row=2, column=2, padx=10, pady=5)

        self.speed_duration_var = tk.StringVar()
        speed_duration_combobox = ttk.Combobox(frame, textvariable=self.speed_duration_var, state="readonly", width=10)
        speed_duration_combobox['values'] = ['0s', '0.2s', '0.5s', '1s', '1.5s', '2s']
        if 'speed_duration' in config['Detection']:
            self.speed_duration_var.set(config['Detection']['speed_duration'])
        else:
            speed_duration_combobox.set('0.5s')
        speed_duration_combobox.grid(row=2, column=3, padx=10, pady=5)

        # Acceleration threshold and duration
        self.acceleration_threshold_var = tk.StringVar()
        if 'acceleration_threshold' in config['Detection']:
            self.acceleration_threshold_var.set(config['Detection']['acceleration_threshold'])
        else:
            self.acceleration_threshold_var.set("0.007")
        acceleration_threshold_entry = ttk.Entry(frame, textvariable=self.acceleration_threshold_var, validate="key",
                                                 validatecommand=(self.validate_range, '%P'))
        acceleration_threshold_entry.grid(row=3, column=1, padx=10, pady=5)

        self.acceleration_direction_var = tk.StringVar()
        acceleration_direction_combobox = ttk.Combobox(frame, textvariable=self.acceleration_direction_var, state="readonly",
                                                      width=10)
        acceleration_direction_combobox['values'] = ['over', 'below']
        if 'acceleration_direction' in config['Detection']:
            self.acceleration_direction_var.set(config['Detection']['acceleration_direction'])
        else:
            acceleration_direction_combobox.set('over')
        acceleration_direction_combobox.grid(row=3, column=2, padx=10, pady=5)

        self.acceleration_duration_var = tk.StringVar()
        acceleration_duration_combobox = ttk.Combobox(frame, textvariable=self.acceleration_duration_var,
                                                      state="readonly", width=10)
        acceleration_duration_combobox['values'] = ['0s', '0.2s', '0.5s', '1s', '1.5s', '2s']
        if 'acceleration_duration' in config['Detection']:
            self.acceleration_duration_var.set(config['Detection']['acceleration_duration'])
        else:
            acceleration_duration_combobox.set('0.5s')
        acceleration_duration_combobox.grid(row=3, column=3, padx=10, pady=5)

        ttk.Label(frame, text='\'Position Detection Setting\' Click on the left \'Position\''). \
            grid(row=4, column=0, columnspan=3, pady=20)
        # Button to retrieve values
        ttk.Button(frame, text="Get Values", command=self.get_selected_values, state='Disabled')

    def get_selected_values(self):
        freezing_threshold = self.freezing_threshold_var.get()
        freezing_duration = self.freezing_duration_var.get()
        speed_threshold = self.speed_threshold_var.get()
        speed_direction = self.speed_direction_var.get()
        speed_duration = self.speed_duration_var.get()
        acceleration_threshold = self.acceleration_threshold_var.get()
        acceleration_direction = self.acceleration_direction_var.get()
        acceleration_duration = self.acceleration_duration_var.get()
        print(f'Freezing - Threshold: {freezing_threshold}, Duration: {freezing_duration}')
        print(f'Speed - Threshold: {speed_threshold}, Direction: {speed_direction}, Duration: {speed_duration}')
        print(f'Acceleration - Threshold: {acceleration_threshold}, Direction: {acceleration_direction}, Duration: {acceleration_duration}')

    def validate_entry_ratio(self, new_value):
        """ Validates that the entry is a number between 0 and 1 """
        if new_value == "":
            return True
        try:
            value = float(new_value)
            if 0 <= value <= 1:
                return True
        except ValueError:
            return False
        return False

    def validate_entry(self, new_value):
        """ Validates that the entry is a number between 0 and 1 """
        if new_value == "":
            return True
        try:
            value = float(new_value)
            if value:
                return True
        except ValueError:
            return False
        return False

    def save_config(self):
        self.config['Detection']['freezing_threshold'] = self.freezing_threshold_var.get()
        self.config['Detection']['freezing_duration'] = self.freezing_duration_var.get()
        self.config['Detection']['speed_threshold'] = self.speed_threshold_var.get()
        self.config['Detection']['speed_direction'] = self.speed_direction_var.get()
        self.config['Detection']['speed_duration'] = self.speed_duration_var.get()
        self.config['Detection']['acceleration_threshold'] = self.acceleration_threshold_var.get()
        self.config['Detection']['acceleration_direction'] = self.acceleration_direction_var.get()
        self.config['Detection']['acceleration_duration'] = self.acceleration_duration_var.get()
        return True


class CloseLoopSettingPage:
    def __init__(self, frame, config):
        self.config = config

        # Duration of each signal (s)
        ttk.Label(frame, text="Duration of each signal (s):").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.duration_signal_var = tk.StringVar()
        if 'duration' in self.config['Close Loop']:
            self.duration_signal_var.set(self.config['Close Loop']['duration'])
        else:
            self.duration_signal_var.set("0.2")
        self.validate_duration_signal = frame.register(self.validate_duration_signal_entry)
        duration_signal_entry = ttk.Entry(frame, textvariable=self.duration_signal_var, validate="key",
                                          validatecommand=(self.validate_duration_signal, '%P'))
        duration_signal_entry.grid(row=0, column=1, padx=10, pady=5)

        # Signal delay after time (s)
        ttk.Label(frame, text="Signal delay after time (s):").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.signal_delay_var = tk.StringVar()
        if 'delay' in self.config['Close Loop']:
            self.signal_delay_var.set(self.config['Close Loop']['delay'])
        else:
            self.signal_delay_var.set("2")
        self.validate_signal_delay = frame.register(self.validate_signal_delay_entry)
        signal_delay_entry = ttk.Entry(frame, textvariable=self.signal_delay_var, validate="key",
                                       validatecommand=(self.validate_signal_delay, '%P'))
        signal_delay_entry.grid(row=2, column=1, padx=10, pady=5)

        # Signal interval (s)
        ttk.Label(frame, text="Signal interval (zero means only once) (s):").grid(row=3, column=0, padx=10, pady=5,
                                                                                  sticky=tk.W)
        self.signal_interval_var = tk.StringVar()
        if 'interval' in self.config['Close Loop']:
            self.signal_interval_var.set(self.config['Close Loop']['interval'])
        else:
            self.signal_interval_var.set("0")
        self.validate_signal_interval = frame.register(self.validate_signal_interval_entry)
        signal_interval_entry = ttk.Entry(frame, textvariable=self.signal_interval_var, validate="key",
                                          validatecommand=(self.validate_signal_interval, '%P'))
        signal_interval_entry.grid(row=3, column=1, padx=10, pady=5)

        # Button to retrieve values
        ttk.Button(frame, text="Get Values", command=self.get_selected_values, state="disabled")

    def get_selected_values(self):
        duration_signal = self.duration_signal_var.get()
        signal_delay = self.signal_delay_var.get()
        signal_interval = self.signal_interval_var.get()
        print(f'Duration: {duration_signal}s, '
              f'Delay: {signal_delay}s, Interval: {signal_interval}s')

    def validate_duration_signal_entry(self, new_value):
        """ Validates that the duration entry is a number between 0 and 1 """
        if new_value == "":
            return True
        try:
            value = float(new_value)
            if 0 <= value <= 1:
                return True
        except ValueError:
            return False
        return False

    def validate_signal_delay_entry(self, new_value):
        """ Validates that the signal delay entry is a number between 0 and 10 """
        if new_value == "":
            return True
        try:
            value = float(new_value)
            if 0 <= value <= 10:
                return True
        except ValueError:
            return False
        return False

    def validate_signal_interval_entry(self, new_value):
        """ Validates that the signal interval entry is a number between 0 and 10 """
        if new_value == "":
            return True
        try:
            value = float(new_value)
            if 0 <= value <= 10:
                return True
        except ValueError:
            return False
        return False

    def save_config(self):
        self.config['Close Loop']['duration'] = self.duration_signal_var.get()
        self.config['Close Loop']['delay'] = self.signal_delay_var.get()
        self.config['Close Loop']['interval'] = self.signal_interval_var.get()
        return True


class SelectedAreaAnalysisSettingPage(BasePictureSelectSettingPage):
    def __init__(self, frame, config, image):
        super().__init__(frame, config, image)
        self.select_area_list = []
        self.init_shape('Selected area analysis')
        ttk.Button(self.button_frame, text='Clear Last', command=self.clear_last_area).pack(pady=(60, 0))

    def set_area_mode_select(self):
        self.mode = 'area_select'
        if self.area_select:
            self.select_area_list.append(self.area_select)
        self.area_select = None
        self.polygon_points_select.clear()

    def clear_last_area(self):
        if self.area_select:
            self.select_area_list.append(self.area_select)
        self.area_select = None
        if len(self.select_area_list) == 0:
            return
        area = self.select_area_list.pop()
        self.canvas.delete(area)

    def save_config(self):
        if self.area_select:
            self.select_area_list.append(self.area_select)
        if len(self.select_area_list) == 0:
            self.config['Selected area analysis'].pop('area_types', None)
            self.config['Selected area analysis'].pop('area_points', None)
            return True
        area_types = []
        area_points = []
        for area in self.select_area_list:
            area_types.append(self.canvas.type(area))
            area_points.append(self.canvas.coords(area))
        self.config['Selected area analysis']['area_types'] = area_types
        self.config['Selected area analysis']['area_points'] = area_points
        return True

    def init_shape(self, setting_name):
        if 'area_types' in self.config[setting_name]:
            area_types = self.config[setting_name]['area_types']
            area_points = self.config[setting_name]['area_points']

            for i, (area_type, points) in enumerate(zip(area_types, area_points)):
                if area_type == 'rectangle':
                    self.select_area_list.append(self.canvas.create_rectangle(points, outline='blue'))
                elif area_type == 'oval':
                    self.select_area_list.append(self.canvas.create_oval(points, outline='blue'))
                elif area_type == 'polygon':
                    self.select_area_list.append(
                        self.canvas.create_polygon(points, outline='blue', fill='', smooth=False))


if __name__ == '__main__':
    root = tk.Tk()
    app = SettingsGUI(root, None, 'Selected area analysis')
    root.mainloop()
