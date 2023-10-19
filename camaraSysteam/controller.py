import classedGimbal as gm

"""
控制器模块
对于云台的算法控制可以在此处完成
"""

"""
PID控制云台
没写好，不能用
"""
class controller_PID:
    # 计算器模块
    class func_Liner:
        def __init__(self,max_speed):
            # self.K = max_speed/0.5
            self.K = max_speed
        # 函数：y=8*x^3*max_speed
        def calculate(self, error):
            print("errte",error)
            print("speed",(error**3)*self.K*8 )
            return (error**3)*self.K*8 
    def __init__(self,max_speed,Y_down,Y_up,running,timing,conn):
        # 控制位 
        self.run = running
        self.timing = timing
        self.conn = conn
        self.g = gm.Gimbal()     
        # 参数初始化
        # self.min_speed = min_speed
        self.max_speed = max_speed 
        # x、y轴控制器
        self.line_x = self.func_Liner(self.max_speed)
        self.line_y = self.func_Liner(self.max_speed)
        #
        # 初始化上一次控制信息，speed
        self.last_stu_x=0
        self.last_stu_y=0

    def controlll_x(self,speed):
        if speed > 0:
            # print("left!",speed)
            self.g.turn_left(int(abs(speed)))
        elif speed < 0:
            # print("right!",speed)
            self.g.turn_right(int(abs(speed)))
        elif speed == 0:
            self.g.turn_stop()
    def controlll_y(self,speed):
        if speed > 0:
            # print("up!",speed)
            self.g.turn_up(int(abs(speed)))
        elif speed < 0:
            # print("down!",speed)
            self.g.turn_down(int(abs(speed)))
        elif speed == 0:
            self.g.turn_stop()
    def control_loop(self):
        while self.timing.value:
            continue
        while self.run.value==1:
            # get message
            message = self.conn.recv()
            if not message:
                self.controlll_x(self.last_stu_x)
                self.controlll_y(self.last_stu_y)
                continue
            # screen_info = message[0]
            # target_position = message[1]
            # # 计算
            # error_x = 0.5 - target_position[0]/screen_info[0]
            # error_y = 0.5 - target_position[1]/screen_info[1]
            # 计算偏差
            error_x = 0.5-message[1][0]/message[0][0]
            error_y = 0.5-message[1][1]/message[0][1]
            # 由偏差得到速度
            speed_x = self.line_x.calculate(error_x)
            speed_y = self.line_y.calculate(error_y)
            self.last_stu_x = speed_x
            self.last_stu_y = speed_y
            # 转动
            self.controlll_x(speed_x)
            self.controlll_y(speed_y)
        print("release control")
        self.g.turn_stop()
        return
    #  测试用，不需要云台转动时，防止pipe无人接收溢出导致报错
    def control_nothing(self):
        while self.run.value:
            mg = self.conn.recv()
            print(mg)
        print("release control")


"""
通过函数控制云台运行
核心计算依靠函数曲线。，负为左，正为右，同理上下
y=speed |         .
        |         .
        | 
        |        .  
        |     .   
        | .
        0——————————————————— 
                            x = error


"""
class controller_func:
    # 计算器模块
    class func_Liner:
        def __init__(self,max_speed):
            # self.K = max_speed/0.5
            self.K = max_speed
        # 函数：y=8*x^3*max_speed
        def calculate(self, error):
            # print("errte",error)
            # print("speed",(error**3)*self.K*8 )
            return (error**3)*self.K*8 
            # if error<-0.05:
            #     return -self.K
            # elif error > 0.05:
            #     return self.K
            # else:
            #     return 0            
    def __init__(self,max_speed,running,timming,conn):
        # 控制位 
        self.run = running
        self.timming = timming
        self.conn = conn
        self.g = gm.Gimbal()     
        # 参数初始化
        # self.min_speed = min_speed
        self.max_speed = max_speed 
        # x、y轴控制器
        self.line_x = self.func_Liner(self.max_speed)
        self.line_y = self.func_Liner(self.max_speed)
        #
        # 初始化上一次控制信息，speed
        self.last_stu_x=0
        self.last_stu_y=0

    def controlll_x(self,speed):
        if speed > 0:
            # print("left!",speed)
            self.g.turn_left(int(abs(speed)))
        elif speed < 0:
            # print("right!",speed)
            self.g.turn_right(int(abs(speed)))
        elif speed == 0:
            self.g.turn_stop()
    def controlll_y(self,speed):
        if speed > 0:
            # print("up!",speed)
            self.g.turn_up(int(abs(speed)))
        elif speed < 0:
            # print("down!",speed)
            self.g.turn_down(int(abs(speed)))
        elif speed == 0:
            self.g.turn_stop()
    def control_loop(self):
        while self.timming.value==1:
            continue
        while self.run.value==1:
            # get message
            message = self.conn.recv()
            if not message:
                self.controlll_x(self.last_stu_x)
                self.controlll_y(self.last_stu_y)
                continue
            # screen_info = message[0]
            # target_position = message[1]
            # # 计算
            # error_x = 0.5 - target_position[0]/screen_info[0]
            # error_y = 0.5 - target_position[1]/screen_info[1]
            # 计算偏差
            error_x = 0.5-message[1][0]/message[0][0]
            error_y = 0.5-message[1][1]/message[0][1]
            # 由偏差得到速度
            speed_x = self.line_x.calculate(error_x)
            speed_y = self.line_y.calculate(error_y)
            self.last_stu_x = speed_x
            self.last_stu_y = speed_y
            # 转动
            self.controlll_x(speed_x)
            self.controlll_y(speed_y)
        print("release control")
        self.g.turn_stop()
        return
    #  测试用，不需要云台转动时，防止pipe无人接收溢出导致报错
    def control_nothing(self):
        while self.run.value:
            mg = self.conn.recv()
            print(mg)
        print("release control")
