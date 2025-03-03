#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Original Author: Arne F. Meyer <arne.f.meyer@gmail.com>
# License: GPLv3

"""
    Control-related functionality.

    For RPi GPIO pinout see https://pinout.xyz. Note that this script uses
    the "Board" pin mode as the "BCM" mode might differ between different
    RPi versions.
"""

from __future__ import print_function

import os
import os.path as op
import time
import traceback
import json
import threading
import zmq
from datetime import datetime

from .camera import CameraGPIO, DetectGPIO
from .streams import NetworkStreamOutput




class ZmqThread(threading.Thread):
    """Handle communication with an open-ephys plugin (or any other zmq client)

    """

    def __init__(self, start_callback, stop_callback, close_callback,
                 parameter_callback, capture_callback):

        super(ZmqThread, self).__init__()

        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.close_callback = close_callback
        self.parameter_callback = parameter_callback
        self.capture_callback = capture_callback

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
            if cmd == 'Start':
                client_ip = str(parts[1])
                print("Received request from: " + client_ip)
                rec_path = self.start_callback(client_ip)

                socket.send_string("Start")

            elif cmd == 'Preview':

                self.parameter_callback('Preview', None)
                socket.send_string('Preview')

            elif cmd == 'StopPreview':

                self.parameter_callback('StopPreview', None)
                socket.send_string('PreviewStopped')

            elif cmd == 'GpioUp':

                self.parameter_callback('GpioUp', None)
                socket.send_string('GPIO UP')

            elif cmd == 'GpioDown':

                self.parameter_callback('GpioDown', None)
                socket.send_string('GPIO DOWN')

            elif cmd == 'GpioTTL':
                self.parameter_callback('GpioTTL', None)
                socket.send_string('GPIO TTL')

            elif cmd == 'Stop':
                socket.send_string('Stopped')
                self.parameter_callback('Stop', None)

            elif cmd == 'Close':

                self.parameter_callback('Close', None)
                socket.send_string('Closing')
                break

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
                socket.send_string('TTL started')
                self.parameter_callback('StartTTL', None)

            elif cmd == 'StopTTL':
                socket.send_string('TTL stopped')
                self.parameter_callback('StopTTL', None)

            elif cmd == 'ResetGains':

                self.parameter_callback('ResetGains', None)
                socket.send_string("Done")

            elif cmd == 'VFlip':

                self.parameter_callback('VFlip', int(parts[1]) > 0)
                socket.send_string("Done")

            elif cmd == 'HFlip':

                self.parameter_callback('HFlip', int(parts[1]) > 0)
                socket.send_string("Done")

            elif cmd == 'Zoom':

                self.parameter_callback('Zoom', [float(p) for p in parts[1:]])
                socket.send_string("Done")

            elif cmd == 'Capture':
                photo_path = self.capture_callback()
                if photo_path is not None:
                    with open(photo_path, 'rb') as file:
                        data = file.read()
                    socket.send(data)
                else:
                    socket.send("Fail")

            else:
                print(cmd)
                socket.send_string("Not handled")


class Controller(object):

    def __init__(self, data_path, **kwargs):

        super(Controller, self).__init__()

        self.data_path = data_path
        self.closed = False

        try:
            self.camera = CameraGPIO(**kwargs)
            self.detect = DetectGPIO()

        except BaseException:
            traceback.print_exc()
            self.camera = None

    def __del__(self):

        self.cleanup()

    @property
    def framerate(self):

        if self.camera is not None:
            return self.camera.framerate

    @framerate.setter
    def framerate(self, fps):

        if self.camera is not None and not self.camera.recording:
            self.camera.framerate = fps

    @property
    def resolution(self):

        if self.camera is not None:
            return self.camera.resolution

    @resolution.setter
    def resolution(self, xy):

        if self.camera is not None and not self.camera.recording:
            self.camera.resolution = xy

    @property
    def vflip(self):

        if self.camera is not None:
            return self.camera.vflip

    @vflip.setter
    def vflip(self, status):

        if self.camera is not None and not self.camera.recording:
            self.camera.vflip = status

    @property
    def hflip(self):

        if self.camera is not None:
            return self.camera.hflip

    @hflip.setter
    def hflip(self, status):

        if self.camera is not None and not self.camera.recording:
            self.camera.hflip = status

    @property
    def zoom(self):

        if self.camera is not None:
            return self.camera.zoom

    @zoom.setter
    def zoom(self, coords):

        if self.camera is not None:
            if len(coords) == 4 and min(coords) >= 0 and max(coords) <= 1:
                self.camera.zoom = coords

    def cleanup(self):

        if self.camera is not None:

            if self.camera.recording:
                print("Controller: stopping recording ")
                self.camera.stop_recording()

            if self.camera.previewing:
                print("Controller: stopping preview")
                self.camera.stop_preview()

            if not self.camera.closed:
                print("Camera: closing")
                self.camera.close()

            print("Controller: deleting camera")
            del self.camera
            self.camera = None

        self.detect.close()

        self.closed = True

    def stop_preview(self):
        self.camera.stop_preview()

    def start_preview(self,
                      warmup=2.,
                      fix_awb_gains=True,
                      fix_exposure_speed=True,
                      **kwargs):

        if self.camera is not None:

            self.camera.awb_mode = 'auto'
            self.camera.exposure_mode = 'auto'

            self.camera.start_preview(**kwargs)

            # wait for camera to "warm up"
            time.sleep(warmup)

            if fix_awb_gains:
                gains = self.camera.awb_gains
                print("fixing awb gains:", gains)
                self.camera.awb_mode = 'off'
                self.camera.awb_gains = gains

            if fix_exposure_speed:
                self.camera.shutter_speed = self.camera.exposure_speed
                self.camera.exposure_mode = 'off'

    def reset_gains(self,
                    warmup=2.,
                    fix_awb_gains=True,
                    fix_exposure_speed=True):

        if self.camera is not None:

            if self.camera.recording:
                self.camera.stop_recording()

            was_previewing = self.camera.previewing
            if self.camera.previewing:
                self.camera.stop_preview()

            if was_previewing:
                self.start_preview(warmup=warmup,
                                   fix_awb_gains=fix_awb_gains,
                                   fix_exposure_speed=fix_exposure_speed)

    def start_recording(self, client_ip, filename='rpicamera_video', quality=23):

        if self.camera is not None and not self.camera.recording:

            rec_path = self.data_path

            print("Saving data to:", rec_path)

            file_base = op.join(rec_path, filename)
            param_file = file_base + '_params.json'

            # parameters and path information
            params = {'rec_path': rec_path,
                      'width': self.camera.resolution.height,
                      'height': self.camera.resolution.height,
                      'framerate': float(self.camera.framerate)}

            with open(param_file, 'w') as f:
                json.dump(params, f, indent=4,
                          sort_keys=True, separators=(',', ': '))

            output_stream = NetworkStreamOutput(address=client_ip)
            print('init finish')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ts_path = op.join(rec_path, f"output_timestamps_{timestamp}.csv")
            self.camera.start_recording(output=output_stream,
                                        ts_path=ts_path,
                                        client_ip=client_ip,
                                        format='mjpeg', 
                                        # format='h264',
                                        quality=quality)

        else:
            rec_path = None

        return rec_path

    def capture(self):
        if self.camera is not None and not self.camera.recording:
            photo_path = os.path.join(self.data_path, "example_photo.jpg")
            self.camera.capture(photo_path)
        else:
            photo_path = None
        return photo_path

    def stop_recording(self):

        if self.camera is not None and self.camera.recording:

            print("Controller: stopping recording")
            self.detect.stop_ttl()
            self.camera.stop_recording()

    def gpio_up(self):
        self.detect.gpio_up()

    def gpio_down(self):
        self.detect.gpio_down()

    def gpio_ttl(self):
        self.detect.gpio_ttl()

    def start_ttl(self):
        self.detect.start_ttl()

    def stop_ttl(self):
        self.detect.stop_ttl()

    def set_GPIO_ttl_params(self, duration, interval):
        self.detect.ttl_time = duration
        self.detect.interval = interval

    def close(self):

        print("Controller: cleaning up")
        self.cleanup()
