import cv2
import requests
import numpy as np
import time
# 通过强行解码得到mjpeg视频流画面
# opencv自带的Videocapture函数对mjpeg支持不好，会出现无法识别边界符的报错
# mjpeg是摄像机自带网页使用的流
# 整合到detect里有困难，要么手撕loadstream，要么手撕detect
# 目前仅测试这种方式可以抓到流
def methods():
    r = requests.get('http://192.168.8.92/mjpeg_stream', stream=True)
    if(r.status_code == 200):
        bytes_arr = bytes()
        frame_count = 0
        start_time = time.time()
        for chunk in r.iter_content(chunk_size=1024):
            bytes_arr += chunk
            a = bytes_arr.find(b'\xff\xd8')
            b = bytes_arr.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes_arr[a:b+2]
                bytes_arr = bytes_arr[b+2:]
                i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                print(i)
                print()
                # 此处的i就是预测需要用的数据结构，可以将此处i放到共享变量，或者队列中供detect使用
                cv2.imshow('i', i)
                frame_count+=1
                end_time = time.time()
                # print("FPS:",frame_count/(end_time-start_time))
                if cv2.waitKey(1) == 27:
                    exit(0)
    else:
        print("Received unexpected status code {}".format(r.status_code))

if __name__ == "__main__":
    methods()