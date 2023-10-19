import cv2
from threading import Thread
# availableBackends = [cv2.videoio_registry.getBackendName(b) for b in cv2.videoio_registry.getBackends()]
# print(availableBackends)
# print(cv2.CAP_OPENCV_MJPEG)

# cap = cv2.VideoCapture()
import numpy as np
import requests
import sys
sys.path.insert(0, './yolov5')

from yolov5.utils.google_utils import attempt_download
from yolov5.models.experimental import attempt_load
from yolov5.utils.datasets import LoadStreams_Mjpeg
class LoadStreams_Mjpeg1:  # just for mjpeg
    def __init__(self, sources="ip", img_size=640, stride=32):
        self.mode = 'Mjpegstream'
        self.img_size = img_size
        self.stride = stride
        self.imgs = [None]
        self.sources = sources
        cap = cv2.VideoCapture(sources)

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = cap.get(cv2.CAP_PROP_FPS) % 100

        _, self.imgs = cap.read()  # guarantee first frame

        thread = Thread(target=self.update, daemon=True)
        print(f' success ({w}x{h} at {self.fps:.2f} FPS).')
        thread.start()
        
    def update(self):
        r = requests.get('http://192.168.8.92/mjpeg_stream', stream=True)
        if(r.status_code == 200):
            bytes_arr = bytes()
            frame_count = 0

            for chunk in r.iter_content(chunk_size=1024):
                bytes_arr += chunk
                a = bytes_arr.find(b'\xff\xd8')
                b = bytes_arr.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    jpg = bytes_arr[a:b+2]
                    bytes_arr = bytes_arr[b+2:]
                    i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    self.imgs = i #更新帧
                    print()
                    # 此处的i就是预测需要用的数据结构，可以将此处i放到共享变量，或者队列中供detect使用
                    # cv2.imshow('i', i)
                    frame_count+=1

                    # print("FPS:",frame_count/(end_time-start_time)
        else:
            print("Received unexpected status code {}".format(r.status_code))

    def __iter__(self):
        self.count = -1
        return self

    def __next__(self):
        self.count += 1
        img0 = self.imgs.copy()
        if cv2.waitKey(1) == ord('q'):  # q to quit
            cv2.destroyAllWindows()
            raise StopIteration

        # Letterbox
        img = [letterbox(x, self.img_size, auto=self.rect, stride=self.stride)[0] for x in img0]

        # Stack
        img = np.stack(img, 0)

        # Convert
        img = img[:, :, :, ::-1].transpose(0, 3, 1, 2)  # BGR to RGB, to bsx3x416x416
        img = np.ascontiguousarray(img)

        return self.sources, img, img0, None

    def __len__(self):
        return 0  # 1E12 frames = 32 streams at 30 FPS for 30 years
    

if __name__ == "__main__":
    dataset = LoadStreams_Mjpeg("http://192.168.8.92/mjpeg_stream", img_size=640, stride=32)
    for i,(path,img,im0s,vid_cap) in enumerate(dataset):
    
        cv2.imshow(path,im0s[0])
    