from flask import Flask,jsonify,send_from_directory
import web_capture
import web_configs
import sys
from progress import RecSysteam
import threading
from multiprocessing import Process
recsysteam = RecSysteam()
app = Flask(__name__)

rec_running = None
control_running = None

cloudInfo = None
# main
@app.route('/')
def hello_world():
    return 'Hello World!'
camaras = []

@app.route('/start')
def startCam():
    # 检测传递信息，某种方式将摄像头列表传递进来
    # 对摄像头分别创建对象
    # camlis = ["rtsp://admin:123456Ab@192.168.1.100:554/Streaming/Channels/102"]
    # for i in range(camlis):
    #     temobj = CamCapOnce(camlis[i])
    #     g.cam_
    # g对象tes
    # adr = configs.camara_adr['camara_1']
    # g.camara = CamCapOnce(adr)
    # g.camara.start_cap()
    print("start Ok")
    adr = web_configs.camara_adr['camara_1']
    camara = web_capture.CamCapOnce(adr)
    camaras.append(camara)
    camara.start_cap()
    
    return 'recoding'

@app.route('/stop')
def stopCam():
    print('stopOk')
    try:
        camara = camaras[0]
    except IndexError:
        return 'erro:no camara woking'
    if camara:
        camara.stop_cap()
        del camara
        _=camaras.pop()
    
        return 'finish'
    
@app.route('/play_video')
def play_video():
    # 获取本地视频文件路径
    video_path = '/video.mp4'
    # 返回视频文件 URL
    return {'video_url': f'http://127.0.0.1:5000/{video_path}'}       

@app.route("/ServeRun")
def ServeRun():
    global rec_running
    if not rec_running:
        rec_running = True

        # thread = Process(target=recsysteam.run_web_api)
        # thread.start()
        recsysteam.run_web_api()
        return jsonify(message="Cap started")
    else:
        return jsonify(message="Rec Already running")

@app.route("/GetControl")
def ControlRun():    
    thread = threading.Thread(target=recsysteam.player_web_api)
    thread.start()
    thread.join()
    return jsonify(message="Controling started")
@app.route('/get_video/<name>', methods=['GET'])
def get_video(name):
    return send_from_directory(r'E:\aconnda\PROJ\yolo_deepsort\camaraSysteam', "output.mp4", as_attachment=False)
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,ssl_context=('2.pem', '1.key'))