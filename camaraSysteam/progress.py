from multiprocessing import Process, Value,Pipe
# import classedGimbal as Gimbal
import keyboard
from teackGlass import Tracker as tr

from cam import camp
import controller as ctrl
import cv2 
import threading
# 最大速度、最小速度，最小速度暂未用到
minSpeed=0x01
maxSpeed=0xcc
class systeam_info:
    # 记录初始化的数据
    id = 0
    start_angle_level_H = 0
    start_angle_level_L = 0
    start_angel_virtical_H = 0
    start_angel_virtical_L = 0
    end_angle_level_H = 0
    end_angle_level_L= 0
    end_angle_virtical_H = 0
    end_angle_virtical_L = 0
# 拍摄的主要程序
class RecSysteam:
    def __init__(self,mode = "nomal") -> None:
        self.mode = mode
        self.init_info = systeam_info()
        self.sender_conn,self.rec_conn = Pipe()#创建发送、接收管道
        self.shared_run = Value('i',1)#控制用共享变量
        self.shared_timing = Value('i',1) 
        self.reached = 0   
        # self.ctrler = ctrl.controller_PID(Kp=0.01,Ki=0,Kd=0,min_speed=minSpeed,max_speed=maxSpeed,\
        #                                     running=self.shared_run,conn=self.rec_conn,) 
        self.tracker = tr(running=self.shared_run,conn=self.sender_conn,timeing=self.shared_timing)

        self.ctrler = ctrl.controller_func(maxSpeed,running=self.shared_run,conn=self.rec_conn,timming=self.shared_timing) 
        # 获得追踪器
        self.tracker.opt.show_vid = True
        # 获得录像器
        self.recler = camp(running=self.shared_run,timming=self.shared_timing)
            
    def __del__(self):
        self.ctrler.g.turn_stop()
        
        #控制模块
    def loc_start(self):
        # 定位起点坐标
        g = self.ctrler.g
        level = g.get_level_angle()
        virtical  = g.get_vertical_angle()
        self.init_info.start_angle_level_H = ord(level[4:5])
        self.init_info.start_angle_level_L = ord(level[5:6])
        self.init_info.start_angel_virtical_H = ord(virtical[4:5])
        self.init_info.start_angel_virtical_L = ord(virtical[5:6])
        print("定位起点！")
    def loc_end(self):
        # 定位终点坐标 
        g = self.ctrler.g
        level = g.get_level_angle()
        virtical  = g.get_vertical_angle()
        self.init_info.end_angle_level_H = ord(level[4:5])
        self.init_info.end_angle_level_L = ord(level[5:6])
        self.init_info.end_angle_virtical_H = ord(virtical[4:5])
        self.init_info.end_angle_virtical_L = ord(virtical[5:6])
        print("定位终点！")
        
    def to_start(self):
        # 云台转移到起点位置
        g = self.ctrler.g
        g.control_level_angle(self.init_info.start_angle_level_H,self.init_info.start_angle_level_L)
        g.control_vertical_angle(self.init_info.start_angel_virtical_H,self.init_info.start_angel_virtical_L)
              
    def to_end(self):
        # 云台转移到终点位置位置
        g = self.ctrler.g
        g.control_level_angle(self.init_info.end_angle_level_H,self.init_info.end_angle_level_L)
        g.control_vertical_angle(self.init_info.end_angle_virtical_H,self.init_info.end_angle_virtical_L)
    # wasd移动相机，r停止，q退出，c查看当前角度信息
    #  j设置起点，k设置终点 
    #  u将云台转动到起点位置，i将云台转动到终点位置
    #  1 开始追踪拍摄
    # def player(self):
    #     print("调试模式开启")
    #     g1 = self.ctrler.g
    #     keyboard.add_hotkey("w",g1.turn_up,args=(0x50,))# 移动
    #     keyboard.add_hotkey("a",g1.turn_left,args=(0x50,))# 移动
    #     keyboard.add_hotkey("d",g1.turn_right,args=(0x50,))# 移动
    #     keyboard.add_hotkey("s",g1.turn_down,args=(0x50,))# 移动
        
    #     keyboard.add_hotkey("r",g1.turn_stop,args=())# 停止
        
    #     keyboard.add_hotkey("c",g1.check_angle,args=())# 查看当前状态
        
    #     keyboard.add_hotkey("j",self.loc_start,args=())# 设置起点
    #     keyboard.add_hotkey("k",self.loc_end,args=())# 设置终点
        
    #     keyboard.add_hotkey("u",self.to_start,args=())# 转到起点
    #     keyboard.add_hotkey("i",self.to_end,args=())# 转到终点
           
    #     # keyboard.add_hotkey("1",self.run,args=())# 启动服务，直到终点

    #     while True:
    #         if keyboard.is_pressed("q"):
    #             # cap.release()
    #             # cv2.destroyAllWindows()        
    #             self.shared_run = 0
    #             self.ctrler.g.turn_stop()
    #             break
    #     # rtsp_thread.join()

    #     print("退出调试模式")
    def player(self):
        print("调试模式开启")
        g1 = self.ctrler.g

        # 定义热键
        hotkeys = {
            "w": lambda: g1.turn_up(0x50),
            "a": lambda: g1.turn_left(0x50),
            "d": lambda: g1.turn_right(0x50),
            "s": lambda: g1.turn_down(0x50),
            "r": g1.turn_stop,
            "c": g1.check_angle,
            "j": self.loc_start,
            "k": self.loc_end,
            "u": self.to_start,
            "i": self.to_end
        }

        # 添加热键
        for key, func in hotkeys.items():
            keyboard.add_hotkey(key, func)

        while True:
            if keyboard.is_pressed("q"):
                # cap.release()
                # cv2.destroyAllWindows()
                self.ctrler.g.turn_stop()
                break

        # 移除热键
        for key in hotkeys.keys():
            keyboard.remove_hotkey(key)
        print("退出调试模式")
    # def player_nothing(self):
    #     print("调试模式开启")
    #     keyboard.add_hotkey("1",self.run,args=())# 启动服务，直到终
    #     while True:
    #         if keyboard.is_pressed("q"):
    #             # cap.release()
    #             # cv2.destroyAllWindows()        
    #             self.shared_run = 0
    #             self.ctrler.g.turn_stop()
    #             break
    #     # rtsp_thread.join()

    #     print("退出调试模式")
    def reach_end(self):
        # 判断是否到达终点范围
        l = self.ctrler.g.process_respone_angel(self.ctrler.g.get_level_angle())
        # v = self.ctrler.g.get_vertical_ang
        nowl = (self.init_info.end_angle_level_H*256+self.init_info.end_angle_level_L)/100
        if l>nowl-10 and l<nowl+10:
            print("reach end!")
            self.reached = 1
            return True
        
        else:
            return False
        
    def run(self):
        self.P_detect =  Process(target=self.tracker.detect)
        self.P_control = Process(target=self.ctrler.control_loop)
        self.P_REC = Process(target=self.recler.recode)
        # 追踪拍摄的主程序
        print("start serve") 
        self.P_REC.start()
        self.P_control.start()
        self.P_detect.start()
        self.shared_timing.value = 0
        print("all process start")               
        while 1:
            key =keyboard.is_pressed("q") 
            self.reach_end()
            if key or self.reached:
                self.shared_run.value = 0
                print("end")
                break
        self.P_REC.join()
        self.to_start()
        self.P_control.join()
        self.P_detect.join()
        print("finished")
        return
    def run_web_api(self):
        print("Got serve requirst, got permission")
        
        thread = threading.Thread(target=self.run)
        thread.start()
        return 
    def player_web_api(self):
        print("Got init requirst, got permission")
        self.player()
        return
        
# 测试，不用管 
def test1():
    sender_conn,rec_conn = Pipe()#创建发送、接受管道
    shared_var = Value('i',1)#控制用共享变量
    # temm = tem(conn=rec_conn,running=shared_var)

    # cam = camp(shared_var)
    # p2 = Process(target=cam.recode)
    # print("build cam")
    # p1 = Process
    # p3 = Process(target=temm.recive_nothing)
    # cam.h246_2_mp4("output.h264","output.mp4")
    # p2.start()
    # p1.start()
    # p3.start()
    while 1:
        key = keyboard.is_pressed("w")
        if(key):
            break
    shared_var.value = 0
    # p1.join()
    # p2.join()
    # p3.join()
def test2():
    system = RecSysteam()
    # system.loc_start()
    # system.player
    # system.player()
    system.run()

if __name__ == "__main__":
    test2()