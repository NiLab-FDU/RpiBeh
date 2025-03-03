import os
import threading

import cv2
import numpy as np
import pandas as pd
import zmq

from client_host.Analysis import get_analysis
from client_host.Custom import Custom_name
from client_host.Utils import Log_thread_begin, Log_thread_finish


class Recorder:
    def __init__(self, controller, frame_buffer, track_buffer, save_dir, trial_name, fps=15, frame_width=640, frame_height=640):
        self.frame_buffer = frame_buffer
        self.frame_buffer_reader_index = frame_buffer.register_reader()

        self.frame_h = frame_width
        self.frame_w = frame_height
        self.save_dir = save_dir
        self.trial_name = trial_name
        self.controller = controller

        self.track_buffer = track_buffer

        self.track_buffer_reader_index = -1
        self.position_detector_buffer_index = -1
        self.freezing_detector_buffer_index = -1
        self.speed_detector_buffer_index = -1
        self.acceleration_detector_buffer_index = -1
        self.custom_detector_buffer_index = -1

        if track_buffer is not None:
            self.track_buffer_reader_index = track_buffer.register_reader()
        if controller.position_detector_buffer is not None:
            self.position_detector_buffer_index = controller.position_detector_buffer.register_reader()
        if controller.freezing_detector_buffer is not None:
            self.freezing_detector_buffer_index = controller.freezing_detector_buffer.register_reader()
        if controller.speed_detector_buffer is not None:
            self.speed_detector_buffer_index = controller.speed_detector_buffer.register_reader()
        if controller.acceleration_detector_buffer is not None:
            self.acceleration_detector_buffer_index = controller.acceleration_detector_buffer.register_reader()
        if controller.custom_detector_buffer is not None:
            self.custom_detector_buffer_index = controller.custom_detector_buffer.register_reader()

        video_file_name = os.path.join(save_dir, trial_name + ".mp4")
        self.detector_file_name = os.path.join(save_dir, trial_name + "_detector.csv")
        self.timestamp_filename = os.path.join(save_dir, trial_name + "_timestamp.csv")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        self.video_out = cv2.VideoWriter(video_file_name, fourcc, fps, (frame_width, frame_height))
        self.joint_names = []

    def set_dlc_joint_names(self, joint_names):
        self.joint_names = joint_names

    def start_thread(self):
        threads = []

        thread1 = threading.Thread(target=self.recording_video)
        thread1.start()
        threads.append(thread1)

        if self.track_buffer_reader_index > -0.5:
            thread = threading.Thread(target=self.recording_track)
            thread.start()
            threads.append(thread)

        if self.position_detector_buffer_index > -0.5:
            thread = threading.Thread(target=self.recording_position_detection)
            thread.start()
            threads.append(thread)

        if self.freezing_detector_buffer_index > -0.5:
            thread = threading.Thread(target=self.recording_freezing_detection)
            thread.start()
            threads.append(thread)

        if self.speed_detector_buffer_index > -0.5:
            thread = threading.Thread(target=self.recording_speed_detection)
            thread.start()
            threads.append(thread)

        if self.acceleration_detector_buffer_index > -0.5:
            thread = threading.Thread(target=self.recording_acceleration_detection)
            thread.start()
            threads.append(thread)

        if self.custom_detector_buffer_index > -0.5:
                thread = threading.Thread(target=self.recording_custom_detection)
                thread.start()
                threads.append(thread)

        for thread in threads:
            thread.join()

        get_analysis(self.controller)

    def start(self):
        thread = threading.Thread(target=self.start_thread)
        thread.start()

    def recording_video(self):
        Log_thread_begin("Recording video")
        while True:
            index, frame = self.frame_buffer.get_data(self.frame_buffer_reader_index)
            if index is None:
                break
            self.video_out.write(frame[1])
        self.video_out.release()
        Log_thread_finish("Finished recording video")

        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.setsockopt(zmq.RCVTIMEO, 5000)
        try:
            socket.bind("tcp://*:5556")
            received_data = socket.recv()
            with open(self.timestamp_filename, "wb") as f:
                f.write(received_data)
            print(f"File received and saved as {self.timestamp_filename}.")
        except zmq.Again:
            print("Timestamp Timeout: No data received within 5 seconds.")
        finally:
            socket.close()
            context.term()

    def recording_process(self, process_buffer, buffer_reader_index, output_file_path, csv_name, recording_name):
        Log_thread_begin(f"Recording {recording_name}")
        process_out_list = []
        input_index_list = []
        while True:
            index, out = process_buffer.get_data(buffer_reader_index)
            if index is None:
                break
            if out is None:
                continue
            input_index_list.append(out[0])
            process_out_list.append(out[1][0])
        input_index_list = np.array(input_index_list)
        process_out_list = np.array(process_out_list)
        process_out_list = process_out_list.reshape(process_out_list.shape[0], -1)
        out_list = np.hstack((input_index_list.reshape(-1, 1), process_out_list))
        if csv_name is not None:
            df = pd.DataFrame(out_list, columns=csv_name)
            df.to_csv(output_file_path, header=True, index=False)
        else:
            df = pd.DataFrame(out_list)
            df.to_csv(output_file_path, header=None, index=False)
        Log_thread_finish(f"Recording {recording_name}")

    def recording_track(self):
        csv_names = ['index', 'time', 'x', 'y']
        for joint_name in self.joint_names:
            csv_names.extend([joint_name + ' x', joint_name + ' y', joint_name + ' likelihood'])
        track_out_file_name = os.path.join(self.save_dir, self.trial_name + "_track_out.csv")
        self.recording_process(self.track_buffer, self.track_buffer_reader_index, track_out_file_name, csv_names, 'Tracking')

    def recording_position_detection(self):
        csv_name = ['index', 'res']
        detector_file_name = os.path.join(self.save_dir, self.trial_name + "_position_detection.csv")
        self.recording_process(self.controller.position_detector_buffer, self.position_detector_buffer_index,
                               detector_file_name, csv_name, 'Position Detection')

    def recording_freezing_detection(self):
        csv_name = ['index', 'res', 'over_th', 'area_sum']
        detector_file_name = os.path.join(self.save_dir, self.trial_name + "_freezing_detection.csv")
        self.recording_process(self.controller.freezing_detector_buffer, self.freezing_detector_buffer_index,
                               detector_file_name, csv_name, 'Freezing Detection')

    def recording_speed_detection(self):
        csv_name = ['index', 'res', 'over_or_below_th', 'speed']
        detector_file_name = os.path.join(self.save_dir, self.trial_name + "_speed_detection.csv")
        self.recording_process(self.controller.speed_detector_buffer, self.speed_detector_buffer_index,
                               detector_file_name, csv_name, 'Speed Detection')

    def recording_acceleration_detection(self):
        csv_name = ['index', 'res', 'over_or_below_th', 'speed', 'acceleration']
        detector_file_name = os.path.join(self.save_dir, self.trial_name + "_acceleration_detection.csv")
        self.recording_process(self.controller.acceleration_detector_buffer, self.acceleration_detector_buffer_index,
                               detector_file_name, csv_name, 'Acceleration Detection')

    def recording_custom_detection(self):
        csv_name = ['index', 'res']
        detector_file_name = os.path.join(self.save_dir, self.trial_name + "_" + Custom_name + "_detection.csv")
        self.recording_process(self.controller.custom_detector_buffer, self.custom_detector_buffer_index,
                               detector_file_name, csv_name, Custom_name + ' Detection')