import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from client_host.Custom import Custom_name, input_data_type

import tkinter as tk
import traceback
from tkinter import ttk, messagebox
from tkinter.ttk import Combobox
from tkinter import filedialog

from client_host.Controller import Controller
from client_host.GUI.ConfigManager import ConfigManager
from client_host.GUI.SettingsGUI import SettingsGUI
from client_host.GUI.validator import validate_connect_button_input, validate_prepare_button_input, \
    validate_non_negative_number, validate_start_button_input


def edit_selected_area_analysis_setting():
    print("Edit selected")
    return False


class MainGUI:
    def __init__(self, root):
        self.root = root
        root.title('name')
        self.config_manager = ConfigManager(self)
        self.config_manager.load_config()
        self.controller = Controller(self.config_manager, self)

        self.menu = MenuGUI(self)
        self.rpi_camera_gui = RpiCameraGUI(self)
        self.realtime_detection_gui = RealtimeDetectionGUI(self)
        self.close_loop_gui = CloseLoopGUI(self)
        self.analysis_gui = AnalysisGUI(self)
        self.record_gui = RecordGUI(self)

        root.config(menu=self.menu.menubar)
        self.rpi_camera_gui.group.pack(anchor='w', pady=10, padx=10, fill='x')
        self.realtime_detection_gui.group.pack(anchor='w', pady=10, padx=10, fill='x')
        self.close_loop_gui.group.pack(anchor='w', pady=10, padx=10, fill='x')
        self.analysis_gui.group.pack(anchor='w', pady=10, padx=10, fill='x')
        self.record_gui.group.pack(anchor='w', pady=10, padx=10, fill='x')

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.config_manager.load_config(file_path)

            self.rpi_camera_gui.set_config()
            self.realtime_detection_gui.set_config()
            self.close_loop_gui.set_config()
            self.analysis_gui.set_config()
            self.record_gui.set_config()

    def save_config(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            self.config_manager.save_config(file_path)

    def get_config(self):
        return {
            'Settings': self.config_manager.get_settings_config(),
            'RpiCamera': self.rpi_camera_gui.get_config(),
            'RealtimeDetection': self.realtime_detection_gui.get_config(),
            'CloseLoop': self.close_loop_gui.get_config(),
            'Analysis': self.analysis_gui.get_config(),
            'Record': self.record_gui.get_config()
        }

    def on_close(self):
        self.config_manager.save_config()
        if self.rpi_camera_gui.connect_state:
            self.rpi_camera_gui.func_connect_button()
        self.root.destroy()

    def disable_for_prepare(self):
        self.menu.disable_all_menu_items()
        self.rpi_camera_gui.rpi_address_entry.configure(state='disabled')
        self.rpi_camera_gui.rpi_port_entry.configure(state='disabled')
        self.rpi_camera_gui.pc_address_entry.configure(state='disabled')
        self.rpi_camera_gui.pc_port_entry.configure(state='disabled')
        self.rpi_camera_gui.connect_button.configure(state='disabled')
        self.rpi_camera_gui.capture_button.configure(state='disabled')
        self.rpi_camera_gui.interest_region_setting.configure(state='disabled')

        for checkbutton in self.realtime_detection_gui.checkbutton_list:
            checkbutton.configure(state='disabled')

        self.close_loop_gui.close_loop_method_combobox.configure(state='disabled')
        self.close_loop_gui.setting_button.configure(state='disabled')

        for checkbutton in self.analysis_gui.checkbutton_list:
            checkbutton.configure(state='disabled')

    def enable_for_prepare(self):
        self.menu.enable_all_menu_items()
        # self.rpi_camera_gui.rpi_address_entry.configure(state='disabled')
        # self.rpi_camera_gui.rpi_port_entry.configure(state='disabled')
        # self.rpi_camera_gui.pc_address_entry.configure(state='disabled')
        # self.rpi_camera_gui.pc_port_entry.configure(state='disabled')
        self.rpi_camera_gui.connect_button.configure(state='normal')
        self.rpi_camera_gui.capture_button.configure(state='normal')
        self.rpi_camera_gui.interest_region_setting.configure(state='normal')

        for checkbutton in self.realtime_detection_gui.checkbutton_list:
            checkbutton.configure(state='normal')

        self.close_loop_gui.close_loop_method_combobox.configure(state='normal')
        self.close_loop_gui.setting_button.configure(state='normal')

        for checkbutton in self.analysis_gui.checkbutton_list:
            checkbutton.configure(state='normal')


class RpiCameraGUI:
    def __init__(self, main_gui: MainGUI):
        self.main_gui = main_gui
        self.connect_state = False
        self.default_style = 'default.TButton'

        self.style = ttk.Style()
        self.style.configure("TButton", padding=6)
        self.style.configure("green.TButton", foreground="green")

        group = ttk.LabelFrame(main_gui.root, text='RpiCamera', padding=(10, 5))
        self.group = group

        self.rpi_address_entry = ttk.Entry(group)
        self.rpi_port_entry = ttk.Entry(group)
        self.pc_address_entry = ttk.Entry(group)
        self.pc_port_entry = ttk.Entry(group)
        self.connect_button = ttk.Button(group, text="Connect", command=self.func_connect_button)
        self.capture_button = ttk.Button(group, text='Capture', command=self.func_capture_button)
        self.interest_region_setting = ttk.Button(group, text='region of interest setting',
                                                  command=lambda: SettingsGUI(self.main_gui.root,
                                                                              self.main_gui.config_manager,
                                                                              'Region of interest'))

        ttk.Label(group, text="address").grid(row=0, column=1, columnspan=2, padx=10, pady=2)
        ttk.Label(group, text="port").grid(row=0, column=3, padx=10, pady=2)
        ttk.Label(group, text="Rpi").grid(row=1, column=0, padx=10, pady=2)
        ttk.Label(group, text="PC").grid(row=2, column=0, padx=10, pady=2)
        self.rpi_address_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=2)
        self.rpi_port_entry.grid(row=1, column=3, padx=10, pady=2)
        self.pc_address_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=2)
        self.pc_port_entry.grid(row=2, column=3, padx=10, pady=2)
        self.connect_button.grid(row=1, column=4, padx=10, pady=2)
        self.capture_button.grid(row=2, column=4, padx=10, pady=2)
        self.interest_region_setting.grid(row=3, column=1, columnspan=2, padx=10, pady=2)
        self.set_config()

    def func_connect_button(self):
        rpi_address = self.rpi_address_entry.get()
        rpi_port = self.rpi_port_entry.get()
        pc_address = self.pc_address_entry.get()
        pc_port = self.pc_port_entry.get()
        resolution_width, resolution_height, framerate = self.main_gui.config_manager.get_camera_config_setting()
        if not validate_connect_button_input(rpi_address, pc_address, rpi_port, pc_port):
            messagebox.showerror("Parameter Error", 'Wrong address or port')
            return
        self.connect_state = not self.connect_state

        self.connect_button.configure(text='Connecting...', style='red.TButton')
        self.connect_button.update()
        try:
            if self.connect_state:
                self.main_gui.controller.init_rpiCamera(rpi_address, rpi_port, pc_address, pc_port,
                                                        resolution_width, resolution_height, framerate)
            else:
                self.main_gui.controller.close_rpiCamera()
        except Exception as e:
            self.connect_state = False
            messagebox.showerror("Connection Failed", str(e))

        self.connect_button.configure(text='Connect')
        if self.connect_state:
            self.rpi_address_entry.configure(state="disabled")
            self.rpi_port_entry.configure(state="disabled")
            self.pc_address_entry.configure(state="disabled")
            self.pc_port_entry.configure(state="disabled")
            self.connect_button.configure(style="green.TButton")
        else:
            self.rpi_address_entry.configure(state="normal")
            self.rpi_port_entry.configure(state="normal")
            self.pc_address_entry.configure(state="normal")
            self.pc_port_entry.configure(state="normal")
            self.connect_button.configure(style=self.default_style)

    def func_capture_button(self):
        try:
            photo = self.main_gui.controller.camera_capture()
            self.main_gui.config_manager.set_image(photo)
        except Exception as e:
            messagebox.showerror("Capture Failed", str(e))

    def get_config(self):
        return {
            'rpi_address': self.rpi_address_entry.get(),
            'rpi_port': self.rpi_port_entry.get(),
            'pc_address': self.pc_address_entry.get(),
            'pc_port': self.pc_port_entry.get()
        }

    def set_config(self):
        config = self.main_gui.config_manager.get_rpi_camera_config()
        self.rpi_address_entry.delete(0, tk.END)
        self.rpi_address_entry.insert(0, config['rpi_address'])
        self.rpi_port_entry.delete(0, tk.END)
        self.rpi_port_entry.insert(0, config['rpi_port'])
        self.pc_address_entry.delete(0, tk.END)
        self.pc_address_entry.insert(0, config['pc_address'])
        self.pc_port_entry.delete(0, tk.END)
        self.pc_port_entry.insert(0, config['pc_port'])


class MenuGUI:
    def __init__(self, main_gui: MainGUI):
        self.main_gui = main_gui
        menubar = tk.Menu(main_gui.root)

        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="save config", command=self.main_gui.save_config)
        filemenu.add_command(label="load config", command=self.main_gui.load_config)
        menubar.add_cascade(label="File", menu=filemenu)

        settingmenu = tk.Menu(menubar, tearoff=False)
        settingmenu.add_command(label="Edit Camera Setting",
                                command=lambda: SettingsGUI(self.main_gui.root, self.main_gui.config_manager, 'Camera'))
        settingmenu.add_command(label="Edit Region of interest Setting",
                                command=lambda: SettingsGUI(self.main_gui.root, self.main_gui.config_manager,
                                                            'Region of interest'))
        settingmenu.add_command(label="Edit Tracking Setting",
                                command=lambda: SettingsGUI(self.main_gui.root, self.main_gui.config_manager,
                                                            'Tracking'))
        settingmenu.add_command(label="Edit Detection Setting",
                                command=lambda: SettingsGUI(self.main_gui.root, self.main_gui.config_manager,
                                                            'Detection'))
        settingmenu.add_command(label="Edit Position Setting",
                                command=lambda: SettingsGUI(self.main_gui.root, self.main_gui.config_manager,
                                                            'Position'))
        settingmenu.add_command(label="Edit Close Loop Setting",
                                command=lambda: SettingsGUI(self.main_gui.root, self.main_gui.config_manager,
                                                            'Close Loop'))
        settingmenu.add_command(label="Edit Selected Area Analysis Setting",
                                command=lambda: SettingsGUI(self.main_gui.root, self.main_gui.config_manager,
                                                            'Selected area analysis'))
        menubar.add_cascade(label='Setting', menu=settingmenu)

        self.menubar = menubar
        self.filemenu = filemenu
        self.settingmenu = settingmenu

    def disable_all_menu_items(self):
        for menu in [self.filemenu, self.settingmenu]:
            menu_items = menu.index('end')
            for i in range(menu_items + 1):
                menu.entryconfig(i, state="disabled")

    def enable_all_menu_items(self):
        for menu in [self.filemenu, self.settingmenu]:
            menu_items = menu.index('end')
            for i in range(menu_items + 1):
                menu.entryconfig(i, state="normal")


class RealtimeDetectionGUI:
    def __init__(self, main_gui: MainGUI):
        self.main_gui = main_gui
        group = ttk.LabelFrame(main_gui.root, text='Realtime Detection', padding=(10, 5))
        self.group = group

        self.tracking_var = tk.BooleanVar(value=False)
        self.freezing_var = tk.BooleanVar(value=False)
        self.speed_var = tk.BooleanVar(value=False)
        self.acceleration_var = tk.BooleanVar(value=False)
        self.position_var = tk.BooleanVar(value=False)
        self.custom_var = tk.BooleanVar(value=False)

        tracking_checkbutton = ttk.Checkbutton(group, text='Tracking', variable=self.tracking_var,
                                               command=self.on_tracking_changed)
        freezing_checkbutton = ttk.Checkbutton(group, text='Freezing', variable=self.freezing_var,
                                               command=self.on_freezing_changed)
        speed_checkbutton = ttk.Checkbutton(group, text='Speed', variable=self.speed_var,
                                            command=lambda: self.on_checkbutton_changed(self.speed_var))
        acceleration_checkbutton = ttk.Checkbutton(group, text='Acceleration', variable=self.acceleration_var,
                                                   command=lambda: self.on_checkbutton_changed(self.acceleration_var))
        position_checkbutton = ttk.Checkbutton(group, text='Position', variable=self.position_var,
                                               command=self.on_position_changed)
        custom_checkbutton = ttk.Checkbutton(group, text=Custom_name, variable=self.custom_var,
                                             command=self.on_custom_change)

        tracking_checkbutton.grid(row=0, column=0, padx=10, pady=2)
        freezing_checkbutton.grid(row=1, column=0, padx=10, pady=2)
        speed_checkbutton.grid(row=1, column=1, padx=10, pady=2)
        acceleration_checkbutton.grid(row=1, column=2, padx=10, pady=2)
        position_checkbutton.grid(row=1, column=3, padx=10, pady=2)
        custom_checkbutton.grid(row=1, column=4, padx=10, pady=2)

        self.checkbutton_list = [tracking_checkbutton, freezing_checkbutton, speed_checkbutton,
                                 acceleration_checkbutton, position_checkbutton, custom_checkbutton]
        self.set_config()

    def on_tracking_changed(self):
        if not self.tracking_var.get():
            self.speed_var.set(False)
            self.acceleration_var.set(False)
            self.position_var.set(False)
            self.freezing_var.set(False)
            self.main_gui.analysis_gui.heat_map_var.set(False)
            self.main_gui.analysis_gui.trajectory_map_var.set(False)
            self.main_gui.analysis_gui.freezing_analysis_var.set(False)
            self.main_gui.analysis_gui.selected_area_analysis_var.set(False)
            if input_data_type != 'frame':
                self.custom_var.set(False)
        self.main_gui.close_loop_gui.update_close_loop_method_values()

    def on_custom_change(self):
        if self.custom_var.get() and input_data_type != 'frame':
            self.tracking_var.set(True)
        self.main_gui.close_loop_gui.update_close_loop_method_values()

    def on_checkbutton_changed(self, var):
        if var.get() and not self.tracking_var.get():
            self.tracking_var.set(True)
        self.main_gui.close_loop_gui.update_close_loop_method_values()

    def on_freezing_changed(self):
        if self.freezing_var.get() and not self.tracking_var.get():
            self.tracking_var.set(True)
        if not self.freezing_var.get():
            self.main_gui.analysis_gui.freezing_analysis_var.set(False)
        self.main_gui.close_loop_gui.update_close_loop_method_values()

    def on_position_changed(self):
        if not self.position_var.get():  # True -> False
            self.main_gui.close_loop_gui.update_close_loop_method_values()
            return
        # False -> True
        res = self.main_gui.config_manager.check_position_detection_setting_exist()
        if res and not self.tracking_var.get():
            self.tracking_var.set(True)
        if not res:
            self.position_var.set(False)
        self.main_gui.close_loop_gui.update_close_loop_method_values()

    def get_config(self):
        return {
            'Tracking Method': self.tracking_var.get(),
            'Freezing Method': self.freezing_var.get(),
            'Speed Method': self.speed_var.get(),
            'Acceleration Method': self.acceleration_var.get(),
            'Position Method': self.position_var.get(),
            'Custom Method': self.custom_var.get(),
        }

    def set_config(self):
        config = self.main_gui.config_manager.get_realtime_detection_config()
        self.tracking_var.set(config['Tracking Method'])
        self.freezing_var.set(config['Freezing Method'])
        self.speed_var.set(config['Speed Method'])
        self.acceleration_var.set(config['Acceleration Method'])
        self.position_var.set(config['Position Method'])
        self.custom_var.set(config['Custom Method'])


class CloseLoopGUI:
    def __init__(self, main_gui: MainGUI):
        self.main_gui = main_gui
        group = ttk.LabelFrame(main_gui.root, text='Close Loop', padding=(10, 5))
        self.group = group

        self.close_loop_method_var = tk.StringVar()
        self.close_loop_method_combobox = Combobox(group, state="readonly", textvariable=self.close_loop_method_var)
        self.close_loop_method_combobox['value'] = 'None'
        self.close_loop_method_combobox.current(0)

        self.setting_button = ttk.Button(group, text='Setting',
                                         command=lambda: SettingsGUI(self.main_gui.root,
                                                                     self.main_gui.config_manager, 'Close Loop'))
        self.close_loop_method_combobox.grid(row=0, column=0, padx=10, pady=2)
        self.setting_button.grid(row=0, column=1, padx=10, pady=2)
        self.set_config()

    def update_close_loop_method_values(self):
        values = ['None']
        if self.main_gui.realtime_detection_gui.freezing_var.get():
            values.append('Freezing')
        if self.main_gui.realtime_detection_gui.speed_var.get():
            values.append('Speed')
        if self.main_gui.realtime_detection_gui.acceleration_var.get():
            values.append('Acceleration')
        if self.main_gui.realtime_detection_gui.position_var.get():
            values.append('Position')
        if self.main_gui.realtime_detection_gui.custom_var.get():
            values.append(Custom_name)
        self.close_loop_method_combobox['values'] = values
        if self.close_loop_method_var.get() not in values:
            self.close_loop_method_combobox.set('None')

    def get_config(self):
        return {
            'Close Loop Method': self.close_loop_method_var.get()
        }

    def set_config(self):
        config = self.main_gui.config_manager.get_close_loop_config()
        self.update_close_loop_method_values()
        self.close_loop_method_var.set(config['Close Loop Method'])


class AnalysisGUI:
    def __init__(self, main_gui: MainGUI):
        self.main_gui = main_gui
        group = ttk.LabelFrame(main_gui.root, text='Analysis', padding=(10, 5))
        self.group = group

        self.heat_map_var = tk.BooleanVar(value=False)
        self.trajectory_map_var = tk.BooleanVar(value=False)
        self.freezing_analysis_var = tk.BooleanVar(value=False)
        self.selected_area_analysis_var = tk.BooleanVar(value=False)

        heat_map_checkbutton = ttk.Checkbutton(group, text='Heat Map', variable=self.heat_map_var,
                                               command=lambda: self.main_gui.realtime_detection_gui.
                                               on_checkbutton_changed(self.heat_map_var))
        trajectory_map_checkbutton = ttk.Checkbutton(group, text='Trajectory Map', variable=self.trajectory_map_var,
                                                     command=lambda: self.main_gui.realtime_detection_gui.
                                                     on_checkbutton_changed(self.trajectory_map_var))
        freezing_analysis_checkbutton = ttk.Checkbutton(group, text='Freezing Analysis',
                                                        variable=self.freezing_analysis_var,
                                                        command=self.on_freezing_analysis_changed)
        selected_area_analysis_checkbutton = ttk.Checkbutton(group, text='Selected Area Analysis',
                                                             variable=self.selected_area_analysis_var,
                                                             command=self.on_selected_area_analysis_changed)

        heat_map_checkbutton.grid(row=0, column=0, padx=10, pady=2)
        trajectory_map_checkbutton.grid(row=0, column=1, padx=10, pady=2)
        freezing_analysis_checkbutton.grid(row=0, column=2, padx=10, pady=2)
        selected_area_analysis_checkbutton.grid(row=0, column=3, padx=10, pady=2)

        self.checkbutton_list = [heat_map_checkbutton, trajectory_map_checkbutton,
                                 freezing_analysis_checkbutton, selected_area_analysis_checkbutton]

        self.set_config()

    def on_freezing_analysis_changed(self):
        self.main_gui.realtime_detection_gui.on_checkbutton_changed(self.freezing_analysis_var)
        if self.freezing_analysis_var.get() and not self.main_gui.realtime_detection_gui.freezing_var.get():
            self.main_gui.realtime_detection_gui.freezing_var.set(True)

    def on_selected_area_analysis_changed(self):
        if not self.selected_area_analysis_var.get():
            return
        res = self.main_gui.config_manager.check_selected_area_analysis_setting_exist()
        if res:
            self.main_gui.realtime_detection_gui.on_checkbutton_changed(self.selected_area_analysis_var)
        else:
            self.selected_area_analysis_var.set(False)

    def get_config(self):
        return {
            'Heat Map': self.heat_map_var.get(),
            'Trajectory Map': self.trajectory_map_var.get(),
            'Freezing Analysis': self.freezing_analysis_var.get(),
            'Selected Area Analysis': self.selected_area_analysis_var.get()
        }

    def set_config(self):
        config = self.main_gui.config_manager.get_analysis_config()
        self.heat_map_var.set(config['Heat Map'])
        self.trajectory_map_var.set(config['Trajectory Map'])
        self.freezing_analysis_var.set(config['Freezing Analysis'])
        self.selected_area_analysis_var.set(config['Selected Area Analysis'])


class RecordGUI:
    def __init__(self, main_gui):
        self.prepare_state = False
        self.record_state = False
        self.default_style = 'default.TButton'

        self.style = ttk.Style()
        self.style.configure("TButton", padding=6)
        self.style.configure("green.TButton", foreground="green")
        self.style.configure("red.TButton", foreground="red")

        self.style.map("green.TButton",
                       foreground=[('disabled', 'green')])
        self.style.map("red.TButton",
                       foreground=[('disabled', 'red')])

        self.main_gui = main_gui
        group = ttk.LabelFrame(main_gui.root, text='Record', padding=(10, 5))
        self.group = group

        self.dir_entry = ttk.Entry(group)
        self.trial_entry = ttk.Entry(group)
        self.validate_time = group.register(validate_non_negative_number)
        self.time_entry = ttk.Entry(group, validate='key', validatecommand=(self.validate_time, '%P'))
        self.dir_browse_button = ttk.Button(group, text='Browse',
                                            command=lambda: self.func_dir_browse_button(self.dir_entry))
        self.prepare_button = ttk.Button(group, text='Prepare', command=self.func_prepare_button)
        self.start_button = ttk.Button(group, text='Start', command=self.func_start_button)
        self.stop_button = ttk.Button(group, text='Stop', command=self.func_stop_button)

        ttk.Label(group, text='Dir:').grid(row=0, column=0, padx=10, pady=2)
        ttk.Label(group, text='Trial:').grid(row=1, column=0, padx=10, pady=2)
        ttk.Label(group, text='Time (s):').grid(row=2, column=0, padx=10, pady=2)
        self.dir_entry.grid(row=0, column=1, padx=10, pady=2)
        self.trial_entry.grid(row=1, column=1, padx=10, pady=2)
        self.time_entry.grid(row=2, column=1, padx=10, pady=2)
        self.dir_browse_button.grid(row=0, column=2, padx=10, pady=2)
        self.prepare_button.grid(row=0, column=3, padx=10, pady=2)
        self.start_button.grid(row=1, column=3, padx=10, pady=2)
        self.stop_button.grid(row=2, column=3, padx=10, pady=2)
        self.set_config()

    def func_dir_browse_button(self, entry):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            entry.delete(0, tk.END)
            entry.insert(0, folder_selected)

    def func_prepare_button(self):
        self.main_gui.config_manager.update_config_manager()
        out = validate_prepare_button_input(self.main_gui.config_manager, self.main_gui.rpi_camera_gui.connect_state)
        if out != 'ok':
            messagebox.showerror("Error", out)
            return

        self.prepare_state = not self.prepare_state

        try:
            if self.prepare_state:
                self.main_gui.controller.camera_preview()
            else:
                self.main_gui.controller.camera_stop_preview()
        except Exception as e:
            self.prepare_state = False
            print(str(e))
            traceback.print_exc()
            messagebox.showerror("Prepare Failed", str(e))

        if self.prepare_state:
            self.main_gui.disable_for_prepare()
            self.prepare_button.configure(style="green.TButton")
        else:
            self.main_gui.enable_for_prepare()
            self.prepare_button.configure(style=self.default_style)

    def func_start_button(self):
        self.main_gui.config_manager.update_config_manager()
        out = validate_start_button_input(self.main_gui.config_manager, self.prepare_state)
        if out != 'ok':
            messagebox.showerror("Error", out)
            return

        try:
            self.main_gui.controller.start_record()
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            messagebox.showerror("Record Start Failed", str(e))
            return

        self.record_state = True
        self.start_button.configure(style='green.TButton')
        self.start_button.update()
        self.stop_button.configure(style='red.TButton')
        self.stop_button.update()
        self.prepare_button.configure(state='disabled')
        self.start_button.configure(state='disabled')
        self.dir_entry.configure(state='disabled')
        self.trial_entry.configure(state='disabled')
        self.time_entry.configure(state='disabled')
        self.dir_browse_button.configure(state='disabled')

    def func_stop_button(self):
        if not self.record_state:
            messagebox.showerror("Record Stop Failed", 'Recording not started')
            return

        try:
            self.main_gui.controller.stop_record()
        except Exception as e:
            messagebox.showerror("Record Stop Failed", str(e))
            return

        self.record_state = False
        self.start_button.configure(style=self.default_style)
        self.stop_button.configure(style=self.default_style)
        self.prepare_button.configure(state='normal')
        self.start_button.configure(state='normal')
        self.dir_entry.configure(state='normal')
        self.trial_entry.configure(state='normal')
        self.time_entry.configure(state='normal')
        self.dir_browse_button.configure(state='normal')

    def get_config(self):
        return {
            'Dir': self.dir_entry.get(),
            'Trial': self.trial_entry.get(),
            'Time': self.time_entry.get()
        }

    def set_config(self):
        config = self.main_gui.config_manager.get_record_config()
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, config['Dir'])
        self.trial_entry.delete(0, tk.END)
        self.trial_entry.insert(0, config['Trial'])
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, config['Time'])


if __name__ == '__main__':
    root = tk.Tk()
    app = MainGUI(root)
    root.mainloop()
