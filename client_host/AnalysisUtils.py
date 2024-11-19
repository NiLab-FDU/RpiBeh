import cv2
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def create_heat_map(mouse_positions, h, w, blur_sig=101):
    heat_map_blur = np.zeros((h, w), np.float32)

    for i in range(len(mouse_positions) - 1):
        x_start = mouse_positions[i][0]
        x_end = mouse_positions[i + 1][0]
        y_start = mouse_positions[i][1]
        y_end = mouse_positions[i + 1][1]
        nPoints = int(np.ceil(np.sqrt((x_end - x_start) ** 2 + (y_end - y_start) ** 2))) + 1
        xvalues = np.round(np.linspace(x_start, x_end, nPoints)).astype(int)
        yvalues = np.round(np.linspace(y_start, y_end, nPoints)).astype(int)

        tmpIdx = (yvalues, xvalues)
        heat_map_blur[tmpIdx] += 1

    heat_map_blur = cv2.GaussianBlur(heat_map_blur, (blur_sig, blur_sig), 0)
    heat_map_blur = cv2.normalize(heat_map_blur, None, 0, 255, cv2.NORM_MINMAX)
    heat_map_colored = cv2.applyColorMap(np.uint8(heat_map_blur), cv2.COLORMAP_JET)
    return heat_map_colored


def create_trajectory_map(mouse_positions, h, w, color=None):
    img = np.ones((h, w, 3), np.uint8) * 255

    n_positions = len(mouse_positions)

    for i in range(1, n_positions):
        start_point = mouse_positions[i - 1]
        end_point = mouse_positions[i]

        if color is None:
            line_color = (255 * i // n_positions, 0, 255 - 255 * i // n_positions)
        else:
            line_color = color

        img = cv2.line(img, start_point, end_point, line_color, 2)

    return img


def create_trajectory_map_with_speed(mouse_positions, h, w, color=None):
    img = np.ones((h, w, 3), np.uint8) * 255
    n_positions = len(mouse_positions)

    if n_positions < 2:
        return img

    speed_list = np.linalg.norm(np.diff(mouse_positions, axis=0), axis=1)
    min_speed, max_speed = np.percentile(speed_list, 1), np.percentile(speed_list, 99)

    if max_speed == min_speed:
        max_speed += 1

    for i in range(1, n_positions):
        start_point, end_point = mouse_positions[i - 1], mouse_positions[i]
        speed = speed_list[i - 1]

        color_index = 255 * (speed - min_speed) / (max_speed - min_speed)
        color_index = np.clip(color_index, 0, 255)
        line_color = (255 - color_index, 0, color_index) if color is None else color
        img = cv2.line(img, start_point, end_point, line_color, 2)

    return img


def get_analysis_figure(df, frame_h, frame_w, trajectory_map_name=None, heat_map_name=None):
    try:
        mouse_positions = df.iloc[:, 2:4].values.tolist()
        mouse_positions = [
            [int(round(value)) if not np.isnan(value) else np.nan for value in row]
            for row in mouse_positions
        ]
        mouse_positions = [row for row in mouse_positions if all(value >= 0 for value in row)]

        trajectory_map = create_trajectory_map_with_speed(mouse_positions, frame_h, frame_w)
        heat_map = create_heat_map(mouse_positions, frame_h, frame_w)

        if trajectory_map_name is not None:
            cv2.imwrite(trajectory_map_name, trajectory_map)
        if heat_map_name is not None:
            cv2.imwrite(heat_map_name, heat_map)

        height = max(trajectory_map.shape[0], heat_map.shape[0])
        width1 = trajectory_map.shape[1]
        width2 = heat_map.shape[1]

        trajectory_map_resized = cv2.resize(trajectory_map, (width1, height))
        heat_map_resized = cv2.resize(heat_map, (width2, height))

        combined_image = np.hstack((trajectory_map_resized, heat_map_resized))

        cv2.imshow('Trajectory and Heat Map', combined_image)
        while True:
            if cv2.getWindowProperty('Trajectory and Heat Map', cv2.WND_PROP_VISIBLE) < 1:
                break
            key = cv2.waitKey(100)
            if key != -1:
                break
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        cv2.destroyAllWindows()


def get_shaded_intervals(data, threshold, over_th_frame_num, over_threshold):
    shaded = np.zeros(len(data), dtype=bool)
    start = None

    for i in range(len(data)):
        if (over_threshold and data[i] > threshold) or (not over_threshold and data[i] < threshold):
            if start is None:
                start = i
        else:
            if start is not None:
                if i - start >= over_th_frame_num:
                    shaded[start:i] = True
                start = None

    # Check the last segment
    if start is not None and len(data) - start >= over_th_frame_num:
        shaded[start:] = True

    return shaded


def plot_figure(time, data, threshold, shaded, save_path, title=''):
    level = sum(shaded) / len(shaded) * 100
    plt.figure(figsize=(10, 6))
    plt.plot(time, data, label='Data Line')
    plt.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold = {threshold}')

    start = None
    for i in range(len(shaded)):
        if shaded[i]:
            if start is None:
                start = i
        else:
            if start is not None:
                plt.axvspan(time[start], time[i - 1], color='gray', alpha=0.3)
                start = None
    if start is not None:
        plt.axvspan(time[start], time[-1], color='gray', alpha=0.3)

    plt.xlabel('Time (sec)')
    plt.title(f'{title}: {level:.2f}%')
    plt.savefig(save_path, dpi=300)
    plt.show()


def get_freezing_figure(filename, save_path, threshold, fps, over_th_frame_num):
    df = pd.read_csv(filename)
    data = df.iloc[:, 3].values.tolist()
    time = np.arange(len(data)) / fps

    shaded = get_shaded_intervals(data, threshold, over_th_frame_num, False)
    plot_figure(time, data, threshold, shaded, save_path, title='Freezing Level')


def get_speed_figure(filename, save_path, threshold, fps, over_threshold):
    df = pd.read_csv(filename)
    data = df.iloc[:, 3].values.tolist()
    time = np.arange(len(data)) / fps

    shaded = get_shaded_intervals(data, threshold, 1, over_threshold)
    plot_figure(time, data, threshold, shaded, save_path, title='Speed Level')


def calculate_area_metrics(func, df, scale_coeff, area_type, area_points):
    time = df.iloc[:, 1].values
    x_coords = df.iloc[:, 2].values
    y_coords = df.iloc[:, 3].values

    num_entries = 0
    entry_times = []
    stay_times = []
    total_stay_time = 0
    area_movement_distances = []
    in_area = False
    last_entry_time = None
    prev_x = x_coords[0]
    prev_y = y_coords[0]
    for i in range(len(time)):
        current_x, current_y = x_coords[i], y_coords[i]
        if np.isnan(current_x) or np.isnan(current_y):
            continue
        if func(area_type, area_points, current_x, current_y):
            if not in_area:
                num_entries += 1
                entry_times.append(time[i])
                last_entry_time = time[i]
                area_movement_distances.append(0)
                print('append 0')
            elif i > 0:
                distance = np.sqrt((current_x - prev_x) ** 2 + (current_y - prev_y) ** 2) * scale_coeff
                area_movement_distances[-1] += distance
            in_area = True
        else:
            if in_area:
                stay_time = time[i] - last_entry_time
                stay_times.append(stay_time)
                total_stay_time += stay_time
                last_entry_time = None
            in_area = False
        prev_x, prev_y = current_x, current_y

    if in_area and last_entry_time is not None:
        stay_time = time[-1] - last_entry_time
        stay_times.append(stay_time)
        total_stay_time += stay_time

    average_stay_time = total_stay_time / num_entries if num_entries > 0 else 0
    total_movement_distance_in_area = sum(area_movement_distances)
    average_movement_distance_in_area = total_movement_distance_in_area / num_entries if num_entries > 0 else 0
    average_speed_in_area = total_movement_distance_in_area / total_stay_time if total_stay_time > 0 else 0

    result = {
        'area_type': area_type,
        'area_points': area_points,
        "num_entries": num_entries,
        "entry_times": entry_times,
        "stay_times": stay_times,
        "total_stay_time": total_stay_time,
        "average_stay_time": average_stay_time,
        "total_movement_distance_in_area": total_movement_distance_in_area,
        "average_movement_distance_in_area": average_movement_distance_in_area,
        "average_speed_in_area": average_speed_in_area
    }

    return result
