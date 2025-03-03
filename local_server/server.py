import threading
import argparse

import cv2
import socket
import time

import zmq

stop_sending = False


def server_send_video(address, port, input_file):
    global stop_sending
    cap = cv2.VideoCapture(input_file)
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"frame rate : {frame_rate}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((address, port))
    frame_num = 0
    expected_frame_time = 1 / frame_rate
    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if (not ret) or stop_sending:
            break
        _, encoded_frame = cv2.imencode('.jpg', frame)
        frame_num += 1
        sock.send(encoded_frame.tobytes())

        time.sleep(frame_num * expected_frame_time - (time.time() - start_time))
    print(f"send frame num:{frame_num}")
    cap.release()
    sock.close()
    stop_sending = False


class ZmqThread(threading.Thread):
    def __init__(self, start_callback, stop_callback, close_callback,
                 parameter_callback):

        super(ZmqThread, self).__init__()

        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.close_callback = close_callback
        self.parameter_callback = parameter_callback

        self.url = 'tcp://*:5555'
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.url)

        self.is_running = False
        self.daemon = True

    def stop_running(self):

        self.is_running = False

    def run(self):

        self.is_running = True

        socket = self.socket

        while self.is_running:
            msg = socket.recv().decode('utf-8')
            parts = msg.split()
            cmd = parts[0]
            if cmd == 'connect':
                socket.send_string('ok')
            elif cmd == 'Start':
                rec_path = self.start_callback()
                if rec_path is None:
                    rec_path = ''
                socket.send_string(rec_path)
            elif cmd == 'Stop':
                self.stop_callback()
                socket.send_string('Stopped')
            elif cmd == 'Close':
                self.parameter_callback('Close', None)
                socket.send_string('Closing')
                break
            elif cmd == 'GpioUp':
                self.parameter_callback('GpioUp', None)
                socket.send_string('GPIO UP')
            elif cmd == 'GpioDown':
                self.parameter_callback('GpioDown', None)
                socket.send_string('GPIO DOWN')
            elif cmd == 'GpioTTL':
                self.parameter_callback('GpioTTL', None)
                socket.send_string('GPIO TTL')
            elif cmd == 'Resolution':
                width = int(parts[1])
                height = int(parts[2])
                self.parameter_callback('Resolution', (width, height))
                socket.send_string("Done")
            elif cmd == 'Framerate':
                fps = float(parts[1])
                self.parameter_callback('Framerate', fps)
                socket.send_string("Done")
            elif cmd == 'TTLParams':
                duration, interval = float(parts[1]), float(parts[2])
                self.parameter_callback('TTLParams', (duration, interval))
                socket.send_string("Done")
            elif cmd == 'StartTTL':
                self.parameter_callback('StartTTL', None)
                socket.send_string('TTL started')
            elif cmd == 'StopTTL':
                self.parameter_callback('StopTTL', None)
                socket.send_string('TTL stopped')
            elif cmd == 'Preview':
                self.parameter_callback('Preview', None)
                socket.send_string('Preview started')
            elif cmd == 'StopPreview':
                self.parameter_callback('StopPreview', None)
                socket.send_string('Preview stopped')
            else:
                print(cmd)
                socket.send_string("Not handled")


def run_plugin(address, input_file):

    def start_cam():
        print("Start cam")
        port = 12397
        thread = threading.Thread(target=server_send_video, args=(address, port, input_file))
        thread.start()

    def stop_cam():
        global stop_sending
        stop_sending = True
        print("stop cam")

    def close_cam():
        print("close cam")

    def set_parameter(name, value):

        if name == 'Framerate':
            print("Setting frame rate to: {} Hz".format(value)),
        elif name == 'Resolution':
            print("Setting resolution to: {}".format(value)),
        elif name == 'VFlip':
            print("Setting vflip to: {}".format(value)),
        elif name == 'HFlip':
            print("Setting hflip to: {}".format(value)),
        elif name == 'ResetGains':
            print("Resetting camera gains")
        elif name == 'Stop':
            print("Stopping camera")
        elif name == 'Close':
            print("Closing camera")
        elif name == 'Zoom':
            print("Setting zoom to:", value)
        elif name == "GpioUp":
            print("GPIO UP")
        elif name == "GpioDown":
            print("GPIO DOWN")
        elif name == "GpioTTL":
            print("GPIO TTL")
        elif name == 'StartTTL':
            print('Start TTL')
        elif name == 'StopTTL':
            print('Stop TTL')
        elif name == 'TTLParams':
            print(f'TTL Params : {value[0]}, {value[1]}')
        elif name == 'Preview':
            print("Start Preview")
        elif name == 'StopPreview':
            print("Stop Preview")

    print("Starting ZMQ thread")
    thread = ZmqThread(start_cam, stop_cam, close_cam, set_parameter)
    thread.start()
    thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Camera Plugin Parameters")
    parser.add_argument('address', type=str, help='The address to connect to the server')
    parser.add_argument('input_file', type=str, help='The input file for the video stream')

    args = parser.parse_args()

    run_plugin(args.address, args.input_file)

