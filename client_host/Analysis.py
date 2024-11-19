import json
import os

import numpy as np
import pandas as pd

from client_host.AnalysisUtils import get_freezing_figure, get_analysis_figure, calculate_area_metrics
from client_host.Utils import point_in_area, point_in_exclude_area, convert_ndarray


def get_analysis(controller):
    analysis_config = controller.config_manager.get_analysis_config()
    frame_w, frame_h, fps = controller.config_manager.get_camera_config_setting()
    save_dir = controller.save_dir
    trial_name = controller.trial_name

    if analysis_config['Heat Map'] or analysis_config['Trajectory Map'] or analysis_config['Selected Area Analysis']:
        track_out_file_name = os.path.join(save_dir, trial_name + "_track_out.csv")
        df = pd.read_csv(track_out_file_name)

        trajectory_map_name, heat_map_name = None, None
        if analysis_config['Heat Map']:
            heat_map_name = os.path.join(save_dir, trial_name + "_heat_map.png")
        if analysis_config['Trajectory Map']:
            trajectory_map_name = os.path.join(save_dir, trial_name + "_trajectory_map.png")
        if analysis_config['Heat Map'] or analysis_config['Trajectory Map']:
            get_analysis_figure(df, frame_h, frame_w, trajectory_map_name, heat_map_name)

        if analysis_config['Selected Area Analysis']:
            save_path = os.path.join(save_dir, trial_name + "_selected_area_analysis.json")
            scale = controller.config_manager.get_scale()
            interest_area_type, interest_area_points = controller.config_manager.get_region_of_interest_area()
            detection_config = controller.config_manager.get_realtime_detection_config()
            res = {}
            metrics = calculate_area_metrics(point_in_area, df, scale, interest_area_type, interest_area_points)
            res['Interest Area'] = metrics
            if detection_config['Position Method']:
                position_area_type, position_area_points = controller.config_manager.get_settings_position_parameters()
                metrics = calculate_area_metrics(point_in_area, df, scale, position_area_type, position_area_points)
                res['Position Area'] = metrics
                metrics = calculate_area_metrics(point_in_exclude_area, df, scale,
                                                 [interest_area_type, position_area_type],
                                                 [interest_area_points, position_area_points])
                res['Exclude Position Area'] = metrics
            selected_area_types, selected_area_points = controller.config_manager.get_settings_selected_area_analysis()
            for i in range(len(selected_area_types)):
                area_type, area_points = selected_area_types[i], np.array(selected_area_points[i])
                metrics = calculate_area_metrics(point_in_area, df, scale, area_type, area_points)
                res[f'Selected Area {i+1}'] = metrics
            with open(save_path, "w") as json_file:
                json.dump(res, json_file, indent=4, default=convert_ndarray)

    if analysis_config['Freezing Analysis']:
        filename = os.path.join(save_dir, trial_name + "_freezing_detection.csv")
        freezing_figure_name = os.path.join(save_dir, trial_name + "_freezing_figure.png")
        threshold, _, over_th_frame_num = controller.freezing_detector.get_params()
        get_freezing_figure(filename, freezing_figure_name, threshold, fps, over_th_frame_num)

    return analysis_config
