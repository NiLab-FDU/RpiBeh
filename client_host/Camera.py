import socket
import threading
import time

import cv2
import numpy as np
import zmq


class RpiCamera(object):
    def __init__(self, controller, address, pc_address, port_rpi, port_video,
                 resolution_width, resolution_height, framerate):
        self.controller = controller
        self.rpi_connected = False
        self.video_ready = False
        self.port_video = port_video
        self.address = address
        self.pc_address = pc_address
        url = "tcp://%s:%s" % (address, port_rpi)
        print(url)
        self.width = resolution_width
        self.height = resolution_height
        self.framerate = framerate
        self.socket = None

        self.context = zmq.Context()
        rpi_socket = self.context.socket(zmq.REQ)

        try:
            rpi_socket.connect(url)
        except Exception as e:
            rpi_socket.close()
            raise e
        self.socket = rpi_socket

        self.set_param()

    def __del__(self):
        if self.socket is not None:
            self.socket.close()
        self.context.term()

    def set_param(self):
        msg = "Resolution {} {}".format(self.width, self.height)
        self.socket.send_string(msg)
        print(self.socket.recv())

        msg = "Framerate {}".format(self.framerate)
        self.socket.send_string(msg)
        print(self.socket.recv())

    def set_ttl_params(self, duration, interval):
        msg = "TTLParams {} {}".format(duration, interval)
        self.socket.send_string(msg)
        print(self.socket.recv())

    def receive_video_frames(self, server, frame_buffer, record_time):
        conn = None
        n_bytes = 0
        frame_num = 0
        try:
            conn, addr = server.accept()
            buffer = b''
            start_time = time.time()

            while True:
                if (record_time > 0) and (time.time() - start_time > record_time):
                    self.controller.record_finish()
                data = conn.recv(self.height * self.width * 3)
                conn.send(b"")
                current_time = time.time() - start_time
                if not data:
                    frame_buffer.add_data(None)
                    self.controller.record_finish()
                    print("No data, now break")
                    break
                buffer += data

                # Find the start and end of the JPEG frame
                start_marker = b'\xff\xd8'
                end_marker = b'\xff\xd9'

                start = buffer.find(start_marker)
                end = buffer.find(end_marker)

                while start != -1 and end != -1:
                    frame_data = buffer[start:end + 2]
                    n_bytes += len(frame_data)
                    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                    frame_buffer.add_data([current_time, frame])
                    frame_num += 1
                    buffer = buffer[end + 2:]
                    start = buffer.find(start_marker)
                    end = buffer.find(end_marker)

        finally:
            print(f"receive frame num: {frame_num}")
            if conn is not None:
                conn.close()

    def start_record(self, record_time, frame_buffer):
        print("now in start record")

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', int(self.port_video)))
        server.listen(1)

        thread = threading.Thread(target=self.receive_video_frames, args=(server, frame_buffer, record_time))
        thread.start()

        try:
            msg = "Start"
            msg += " " + self.pc_address
            self.socket.send_string(msg)
            print(self.socket.recv())
        finally:
            pass
        # finally:
        #     self.socket.close()

    def stop_record(self):
        msg = "Stop"
        print("send string Stop")
        self.socket.send_string(msg)
        print(self.socket.recv())

    def camera_preview(self):
        msg = "Preview"
        self.set_param()
        self.socket.send_string(msg)
        print(self.socket.recv())

    def camera_stop_preview(self):
        msg = "StopPreview"
        self.socket.send_string(msg)
        print(self.socket.recv())

    def gpio_up(self):
        msg = "GpioUp"
        self.socket.send_string(msg)
        print(self.socket.recv())

    def gpio_down(self):
        msg = "GpioDown"
        self.socket.send_string(msg)
        print(self.socket.recv())

    def gpio_ttl(self):
        msg = "GpioTTL"
        self.socket.send_string(msg)
        print(self.socket.recv())

    def gpio_start(self):
        self.socket.send_string('StartTTL')
        print(self.socket.recv())

    def gpio_stop(self):
        self.socket.send_string('StopTTL')
        print(self.socket.recv())

    def capture_photo(self):
        if self.address == "127.0.0.1":
            photo_path = r"background_image.png"
            image = cv2.imread(photo_path)
            return image
        msg = "Capture"
        self.socket.send_string(msg)
        data = self.socket.recv()
        nparr = np.frombuffer(data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        print(image.shape)
        return image

    def get_framerate(self):
        return self.framerate

    def get_frame_width(self):
        return self.width

    def get_frame_height(self):
        return self.height

    def close(self):
        self.camera_stop_preview()
        msg = "Close"
        self.socket.send_string(msg)
        print(self.socket.recv())
        if self.socket is not None:
            self.socket.close()
