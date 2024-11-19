import os
import re

from client_host.GUI import ConfigManager


def is_valid_ip(ip):
    def is_valid_ipv4(ip):
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        return re.match(ipv4_pattern, ip) is not None

    def is_valid_ipv6(ip):
        ipv6_pattern = r'^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4})|(([0-9a-fA-F]{1,4}:){6}:[0-9a-fA-F]{1,4})|' \
                       r'(([0-9a-fA-F]{1,4}:){5}:([0-9a-fA-F]{1,4}:){1,4})|' \
                       r'(([0-9a-fA-F]{1,4}:){4}:([0-9a-fA-F]{1,4}:){1,5})|' \
                       r'(([0-9a-fA-F]{1,4}:){3}:([0-9a-fA-F]{1,4}:){1,6})|' \
                       r'(([0-9a-fA-F]{1,4}:){2}:([0-9a-fA-F]{1,4}:){1,7})|' \
                       r'(([0-9a-fA-F]{1,4}:){1}:([0-9a-fA-F]{1,4}:){1,8})|' \
                       r'(:((:[0-9a-fA-F]{1,4}){1,8})|:)|' \
                       r'fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|' \
                       r'::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|' \
                       r'1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|' \
                       r'1{0,1}[0-9]){0,1}[0-9]|' \
                       r'([0-9a-fA-F]{1,4}:){1,4}:([0-9a-fA-F]{1,4}:){1,4}|' \
                       r'([0-9a-fA-F]{1,4}:){1,4}:([0-9a-fA-F]{1,4}))$'
        return re.match(ipv6_pattern, ip) is not None

    return is_valid_ipv4(ip) or is_valid_ipv6(ip)


def is_valid_port(port_str):
    port_pattern = r'^[0-9]{1,5}$'
    if re.match(port_pattern, port_str):
        port = int(port_str)
        if 0 <= port <= 65535:
            return True
    return False


def is_valid_folder_path(path):
    return os.path.isdir(path)


def is_valid_filename(filename):
    pattern = r"^[A-Za-z0-9_\-\.]+$"
    return re.match(pattern, filename) is not None


def validate_connect_button_input(rpi_address, pc_address, rpi_port, pc_port):
    return is_valid_ip(rpi_address) and is_valid_port(rpi_port) and is_valid_ip(pc_address) and is_valid_port(pc_port)


def validate_prepare_button_input(config_manager: ConfigManager, connect_state: bool):
    if not connect_state:
        return 'Connect Camera First'

    if config_manager.get_background_image() is None:
        return 'Load Background Image First'

    settings_config = config_manager.get_settings_config()
    realtime_detection_config = config_manager.get_realtime_detection_config()
    close_loop_config = config_manager.get_close_loop_config()
    analysis_config = config_manager.get_analysis_config()

    # analysis & realtime detection
    if not realtime_detection_config['Tracking Method']:
        if not all(value is False for value in realtime_detection_config.values()) or \
                not all(value is False for value in analysis_config.values()):
            return 'Realtime detection: Tracking Method need be Selected'

    if analysis_config['Freezing Analysis'] and not realtime_detection_config['Freezing Method']:
        return 'Realtime detection: Freezing Method need be Selected'

    # close loop & realtime detection
    close_loop_method = close_loop_config['Close Loop Method']
    if close_loop_method == 'Freezing' and not realtime_detection_config['Freezing Method']:
        return 'Realtime detection: Freezing Method need be Selected'
    if close_loop_method == 'Speed' and not realtime_detection_config['Speed Method']:
        return 'Realtime detection: Speed Method need be Selected'
    if close_loop_method == 'Acceleration' and not realtime_detection_config['Acceleration Method']:
        return 'Realtime detection: Acceleration Method need be Selected'
    if close_loop_method == 'Position' and not realtime_detection_config['Position Method']:
        return 'Realtime detection: Position Method need be Selected'

    # settings
    if ('real distance' not in settings_config['Region of interest']) or \
            len(settings_config['Region of interest']['real distance']) == 0:
        return 'Settings: Region of interest - real distance needs to be set'
    if 'area_type' not in settings_config['Region of interest']:
        return 'Settings: Region of interest - area needs to be drawn'
    if 'line' not in settings_config['Region of interest']:
        return 'Settings: Region of interest - line needs to be drawn'

    if realtime_detection_config['Tracking Method'] and settings_config['Tracking']['method'] == 'DLC_live':
        if not settings_config['Tracking']['detection_result']:
            return 'Settings: Tracking - DLC needs to be load'
        if all(value is False for value in settings_config['Tracking']['key_points']):
            return 'Settings: Tracking - At least one Key point needs to be selected'

    if close_loop_method == 'Freezing' and len(settings_config['Detection']['freezing_threshold']) == 0:
        return 'Settings: Detection - Freezing threshold needs to be set'
    if close_loop_method == 'Speed' and len(settings_config['Detection']['speed_threshold']) == 0:
        return 'Settings: Detection - Speed threshold needs to be set'
    if close_loop_method == 'Acceleration' and len(settings_config['Detection']['acceleration_threshold']) == 0:
        return 'Settings: Detection - Acceleration threshold needs to be set'
    if close_loop_method == 'Position' and ('area_type' not in settings_config['Position']):
        return 'Settings: Position - Position area needs to be set'
    if close_loop_method != 'None' and (len(settings_config['Close Loop']['duration']) == 0
                                        or len(settings_config['Close Loop']['delay']) == 0
                                        or len(settings_config['Close Loop']['interval']) == 0):
        return 'Settings: Close Loop - Settings need to be set'
    if analysis_config['Selected Area Analysis'] and 'area_types' not in settings_config['Selected area analysis']:
        return 'Settings: Selected Area Analysis - Areas need to be set'

    return 'ok'


def validate_start_button_input(config_manager: ConfigManager, prepare_start: bool):
    if not prepare_start:
        return 'Prepare not completed'

    record_config = config_manager.get_record_config()
    if len(record_config['Dir']) == 0:
        return 'Record - Directory needs to be set'
    if len(record_config['Trial']) == 0:
        return 'Record - Trial name needs to be set'
    if len(record_config['Time']) == 0:
        return 'Record - Time needs to be set'
    if not os.path.exists(record_config['Dir']):
        return 'Record - Directory does not exist'

    return 'ok'


def validate_non_negative_number(new_value):
    """ Validates that the signal delay entry is a number >= 0 """
    if new_value == "":
        return True
    try:
        value = float(new_value)
        if 0 <= value:
            return True
    except ValueError:
        return False
    return False
