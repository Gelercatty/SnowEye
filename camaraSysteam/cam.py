import cv2
from multiprocessing import Value
import urllib.request
import numpy as np
class camp:
    source = "rtsp://192.168.8.92/live_stream"
    def __init__(self,running,timming) -> None:
        self.run = running
        self.timing = timming
    def recode(self):
        # URL of the H.264 network video stream
        video_url = self.source

        # # Output file name
        output_file = "output.mp4"
        # Open the video stream
        cap = cv2.VideoCapture(video_url)
        print("cam start REC")
        # Get the video stream's properties
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        # Create the video writer
        fourcc = cv2.VideoWriter_fourcc(*"H264")
        out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))
        while self.timing.value:
            continue
        while self.run.value==1 :
            ret, frame = cap.read()
            n = 0
            if ret:
                # frame = cv2.resize(frame, (200,200))
                # Display the frame
                cv2.imshow(str(n), frame)
                out.write(frame)
            else:
                print("rec wrong")
                break
        print("rec stopping")
        cap.release()
        out.release()
        # Close all OpenCV windows
        cv2.destroyAllWindows()
        print("REC done")
        return
