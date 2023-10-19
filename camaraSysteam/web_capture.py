import cv2
import uuid
from flask import g,send_file
import web_configs
import threading

class CamCapOnce:
    def __init__(self, rtsp_addr):
        self.capturing = False
        self.filename = str('video') + ".mp4"

        self.cap = cv2.VideoCapture(rtsp_addr)
        self.frame_s = self.cap.get(5)
        self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.size = (
            int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        )
        self.ret, self.frame = self.cap.read()
        self.video_writer = cv2.VideoWriter(
            self.filename, self.fourcc, self.frame_s, self.size, True
        )

        self.thread_cap = None
        self.thread_cam_stop = None

    def __del__(self):
        self.video_writer.release()
        self.cap.release()

        if self.thread_cap:
            self.thread_cap.join()
        if self.thread_cam_stop:
            self.thread_cam_stop.join()

    def start_cap(self):
        if self.capturing:
            return
        self.capturing = True
        self.thread_cap = threading.Thread(
            target=self._start_cap, name='capture')
        self.thread_cap.setDaemon(True)
        self.thread_cap.start()

    def _start_cap(self):
        while self.ret and self.capturing:
            self.ret, self.frame = self.cap.read()
            img = cv2.resize(self.frame, (1920, 1080),
                             interpolation=cv2.INTER_LINEAR)
            self.video_writer.write(self.frame)

    def stop_cap(self):
        if not self.capturing:
            return
        self.capturing = False
        self.thread_cam_stop = threading.Thread(
            target=self._stop_cap, name='camStop')
        self.thread_cam_stop.start()

    def _stop_cap(self):
        self.video_writer.release()
        self.cap.release()

