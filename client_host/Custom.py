Custom_name = 'CustomName'

# 'frame', 'xy', 'dlc-live key points'
input_data_type = 'dlc-live key points'


def get_res_frame(frame, timestamp, scale, area_type, area_points):
    print('get_res_frame')
    print(frame.shape)  # (640, 640, 3)
    print(timestamp)  # sec
    return False


def get_res_xy(x, y, timestamp, scale, area_type, area_points):
    print('get_res_xy')
    print(f"x:{x} y:{y} timestamp:{timestamp}")
    return False


def get_res_dlc(point_list, timestamp, scale, area_type, area_points):
    print(point_list.shape)  # (n, 3)  : x, y, likelihood
    print('get_res_dlc')
    return False

