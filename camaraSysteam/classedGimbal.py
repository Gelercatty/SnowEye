import sys
import struct
import socket
import keyboard

class PelcoDProtocol:
    def __init__(self):
        self.flag = 0xFF  # 1 byte, frame start flag
        self.addr = 0x00  # 1 byte, PTZ address
        self.cmd1 = 0x00  # 1 byte, command code 1
        self.cmd2 = 0x00  # 1 byte, command code 2
        self.data1 = 0x00  # 1 byte, data code 1
        self.data2 = 0x00  # 1 byte, data code 2

        self.check = 0x00  # 1 byte, checksum

"""
class HYPTZDataPack:
    def __init__(self):
        self.head = 0xFF  # 1 byte, header
        self.addr = 0x00  # 1 byte, PTZ address
        self.cmd_type = 0x00  # 1 byte, command type
        self.cmd_func = 0x00  # 1 byte, command function
        self.cmd_len = 0x00  # 2 bytes, protocol data length
        self.head_crc = 0x00  # 4 bytes, header checksum (sum of header bytes)
        self.cmd_data = b''  # variable-length, specific data to be transmitted
"""

#--------------------------------------------------------------------------------
# 校验码计算

# 传入：待校验的数据、数据的长度；返回：一个校验位
# 功能：累加和校验(、cmd1、cmd2、data1、data2累加和)
def pelco_d_check(data):
    data.check = (
        data.addr + data.cmd1 + data.cmd2 + data.data1 + data.data2
        ) % 256
    return data.check

"""
def pelco_d_check(data, length):
    cs = 0
    for i in range(1, length - 1):
        cs += data[i]
    return cs
"""

# 传入：一个指向HYPTZDataPack结构体的指针；返回：一个校验值
# 功能：协议包头校验码计算
def edit_cfg_file_head_crc(pack):
    len = len(pack) - 4 - 1  # sizeof(HYPTZDataPack) - sizeof(unsigned int) - sizeof(unsigned char)
    crc = 0
    for len_count in range(len):
        crc += pack[len_count]
    return crc

# 传入：一个指向HYPTZDataPack结构体的指针；返回：一个校验值
# 功能：协议总校验码计算
def ptz_udp_data_pack_a_crc(pack):
    len = len(pack) - 1 + pack.cmd_len  # sizeof(HYPTZDataPack) - 1 + pack.cmd_len
    crc = 0
    for len_count in range(len):
        crc += pack[len_count]
    return crc

#---------------------------------------------------------------------------------
class Gimbal:
    def __init__(self):
        self.addr = 0x01
        self.yutanip = "192.168.8.200"  #其他摄像头需要改
        self.portNo = 6666
        #------------------------------
        self.EDIT_IP = 0x01
        self.EDIT_MAC = 0x02
        self.EDIT_NETMASK = 0x03
        self.EDIT_GATEWAY = 0x04
        #self.EDIT_TERM_IP = 0x05
        #self.EDIT_WEB_IP = 0x06
        #self.EDIT_A9_IP = 0x07
        #self.EDIT_HARDWAREVER = 0x08
        #self.EDIT_CMD_ID = 0x09
        #self.EDIT_COMPONENT_ID = 0x0A


    #定义一个函数，用于发送PelcoDProtocol数据
    def send_data(self, data):
        #创建一个UDP套接字对象
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(3)
        #将PelcoDProtocol数据转换为字节串
        senddata = bytes([
            data.flag, data.addr, 
            data.cmd1, data.cmd2,
            data.data1, data.data2, 
            data.check
            ])
        #发送数据到指定的地址和端口号
        s.sendto(senddata, (self.yutanip, self.portNo))
        #关闭套接字对象
        response_data,adr = s.recvfrom(1024)
        s.close()
        return response_data

        #定义一个函数，用于发送HYPTZDataPack数据
        """
        def send_data(data,len):
            #创建一个UDP套接字对象
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #将HYPTZDataPack数据转换为字节串
            senddata = bytes([
                data.head, data.addr,
                data.cmd_type, data.cmd_func,
                data.cmd_len, data.head_crc,
                data.cmd_data,
                ])
            #发送数据到指定的地址和端口号
            s.sendto(senddata, (yutanip, 6666))
            #关闭套接字对象
            s.close()
            return
        """


    # 配置文件修改

    # 传入：要修改的配置文件内容、要编辑的配置文件类型；作用：根据输入的参数设置相关的结构体字段，并生成一个发送缓冲区send_buff用于发送数据，以供后续发送使用
    # 功能：修改配置文件
    """
    def edit_cfg_file(self, data, content):
        send_buff = bytearray(500)

        length = len(data)

        p = HYPTZDataPack()

        p.head = 0xFF
        p.addr = 0xC8  # Example PTZ address
        p.cmd_type = 0x01

        switcher = {
            self.EDIT_IP: 0x01,
            self.EDIT_MAC: 0x02,
            self.EDIT_NETMASK: 0x03,
            self.EDIT_GATEWAY: 0x04
        }
        p.cmd_func = switcher.get(content, 0x00)

        p.cmd_len = length
        p.head_crc = edit_cfg_file_head_crc(p)
        if length > 0:
            p.cmd_data = data.encode('utf-8')

        len1 = sys.getsizeof(HYPTZDataPack) - 1 + length
        struct.pack_into("<I", send_buff, len1, ptz_udp_data_pack_a_crc(p))
        len1 = len1 + struct.calcsize("I")
        send_buff[len1] = 0x16
        len2 = len1 + struct.calcsize("b")

        # 通过以太网/485/422接口发送
        self.send_data(send_buff, len2)
    """


    def turn_up(self, V_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x08
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = V_speed
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def turn_down(self, V_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x10
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = V_speed
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def turn_left(self, H_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x04
        pelco_d_pack.data1 = H_speed
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def turn_right(self, H_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x02
        pelco_d_pack.data1 = H_speed
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def turn_leftup(self, H_speed, V_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x0C
        pelco_d_pack.data1 = H_speed
        pelco_d_pack.data2 = V_speed
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def turn_leftdown(self, H_speed, V_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x14
        pelco_d_pack.data1 = H_speed
        pelco_d_pack.data2 = V_speed
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def turn_rightup(self, H_speed, V_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x0A
        pelco_d_pack.data1 = H_speed
        pelco_d_pack.data2 = V_speed
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def turn_rightdown(self, H_speed, V_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x12
        pelco_d_pack.data1 = H_speed
        pelco_d_pack.data2 = V_speed
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def auto_left(self, H_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x04
        pelco_d_pack.data1 = H_speed
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def auto_right(self, H_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x02
        pelco_d_pack.data1 = H_speed
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def turn_stop(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x00
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)


    # 角度获取（水平、竖直）
    def process_respone_angel(self,respone):
        H_HAngle = ord(respone[4:5])
        H_LAngle = ord(respone[5:6])
         # 现在我们可以将它们组合成一个16位的整数
        angle_int = H_HAngle * 256 + H_LAngle

        # 由于设备将角度放大了100倍，所以我们需要将它除以100
        angle_deg = angle_int / 100.0

        # 现在angle_deg应该是以度为单位的角度
        return angle_deg
    # 传入：云台的地址；作用：请求获取云台的角度信息,返回360度下的数
    def get_level_angle(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x51
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        a = self.send_data(pelco_d_pack)
        return a
    def get_vertical_angle(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x53
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)
        a = self.send_data(pelco_d_pack)
        return a

    # 云台角度控制（水平、竖直、右转、左转、右转一圈、左转一圈）

    # data_high：角度放大100倍取整后的高8位、data_low：角度放大100倍取整后的低8位
    # 传入：云台的地址、角度*100的二进制高低八位、水平转速；作用：云台角度控制
    def control_level_angle(self, data_high, data_low):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x4b
        pelco_d_pack.data1 = data_high
        pelco_d_pack.data2 = data_low
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def control_vertical_angle(self, data_high, data_low):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x4d
        pelco_d_pack.data1 = data_high
        pelco_d_pack.data2 = data_low
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def control_right_angle(self, data_high, data_low):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xbd
        pelco_d_pack.cmd2 = 0x00
        pelco_d_pack.data1 = data_high
        pelco_d_pack.data2 = data_low
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def control_left_angle(self, data_high, data_low):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xbd
        pelco_d_pack.cmd2 = 0x01
        pelco_d_pack.data1 = data_high
        pelco_d_pack.data2 = data_low
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def control_right_angle_cycle(self, H_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xbd
        pelco_d_pack.cmd2 = 0x02
        pelco_d_pack.data1 = H_speed
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def control_left_angle_cycle(self, H_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xbd
        pelco_d_pack.cmd2 = 0x03
        pelco_d_pack.data1 = H_speed
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)




    # 区域扫描设置

    # Num：扫描编号；data_high：角度放大100倍取整后的高8位、data_low：角度放大100倍取整后的低8位；enable=1：使能相应区域；pause=1：停止区域扫描；single_step=1：单步扫描模式；H_time：停止时间高8位、L_time：停止时间低8位
    # 水平扫描始终、竖直扫描始终（auto和带角度的区别？视频设置、角度设置？），水平扫描间隔角度、竖直扫描间隔角度，扫描速度，单步扫描停止时间，启动多区域、单区域扫描，使能区域扫描，停止/恢复区域扫描，关闭扫描，扫描模式（单步/连续）
    def auto_set_hori_scan_start(self, Num):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xe6
        pelco_d_pack.cmd2 = Num
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def auto_set_hori_scan_end(self, Num):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xe7
        pelco_d_pack.cmd2 = Num
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def auto_set_vert_scan_start(self, Num):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xe8
        pelco_d_pack.cmd2 = Num
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def auto_set_vert_scan_end(self, Num):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xe9
        pelco_d_pack.cmd2 = Num
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def set_hori_scan_start(self, Num, data_high, data_low):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf7
        pelco_d_pack.cmd2 = Num
        pelco_d_pack.data1 = data_high
        pelco_d_pack.data2 = data_low
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def set_hori_scan_end(self, Num, data_high, data_low):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf8
        pelco_d_pack.cmd2 = Num
        pelco_d_pack.data1 = data_high
        pelco_d_pack.data2 = data_low
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def set_vert_scan_start(self, Num, data_high, data_low):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf9
        pelco_d_pack.cmd2 = Num
        pelco_d_pack.data1 = data_high
        pelco_d_pack.data2 = data_low
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def set_vert_scan_end(self, Num, data_high, data_low):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xfa
        pelco_d_pack.cmd2 = Num
        pelco_d_pack.data1 = data_high
        pelco_d_pack.data2 = data_low
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def set_hori_scan_inter(self, Num, data_high, data_low):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xfb
        pelco_d_pack.cmd2 = Num
        pelco_d_pack.data1 = data_high
        pelco_d_pack.data2 = data_low
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def set_vert_scan_inter(self, Num, data_high, data_low):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xfc
        pelco_d_pack.cmd2 = Num
        pelco_d_pack.data1 = data_high
        pelco_d_pack.data2 = data_low
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def set_scan_speed(self, Num, H_speed, V_speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xfd
        pelco_d_pack.cmd2 = Num
        pelco_d_pack.data1 = H_speed
        pelco_d_pack.data2 = V_speed
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def set_scan_stoptime(self, Num, H_time, L_time):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xfd
        pelco_d_pack.cmd2 = Num
        pelco_d_pack.data1 = H_time
        pelco_d_pack.data2 = L_time
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def start_scan_m(self, Num1, Num2):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf5
        pelco_d_pack.cmd2 = 0x02
        pelco_d_pack.data1 = Num1
        pelco_d_pack.data2 = Num2
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def start_scan_s(self, Num):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf5
        pelco_d_pack.cmd2 = 0x01
        pelco_d_pack.data1 = Num
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def scan_enable(self, Num, enable):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf4
        pelco_d_pack.cmd2 = Num
        if enable == 1:              # 1 使能
            pelco_d_pack.data1 = 0x01
        else:                       # 0 失能
            pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def scan_pause_continue(self, pause):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf5
        if pause == 1:              # 1 停止扫描
            pelco_d_pack.cmd2 = 0x03
        else:                      # 0 恢复扫描
            pelco_d_pack.cmd2 = 0x04
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def scan_close(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf5
        pelco_d_pack.cmd2 = 0x05
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def scan_mode(self, Num, single_step):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf5
        pelco_d_pack.cmd2 = 0x06
        pelco_d_pack.data1 = Num
        if single_step == 1:         # 1 单步扫描
            pelco_d_pack.data2 = 0x02
        else:                       # 0 连续扫描
            pelco_d_pack.data2 = 0x01
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)


    # 预置位扫描设置

    #  PP_num：预置位编号；once=1：启动一次预置位扫描，=0：启动且连续；pause=1：预置位扫描停止，=0恢复；H_time：停止时间高8位、L_time：停止时间低8位
    # 视频设置，召回（调用），删除预置位，角度设置水平、竖直，设置预置位停止时间，设置到达预置位速度，启动/停止/恢复预置位扫描，关闭预置位扫描
    def auto_set_preset_point(self, PP_num):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x03
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = PP_num
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def recall_preset_point(self, PP_num):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x07
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = PP_num
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def del_preset_point(self, PP_num):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0x00
        pelco_d_pack.cmd2 = 0x05
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = PP_num
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def set_hori_preset_point(self, PP_num, data_high, data_low):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xe4
        pelco_d_pack.cmd2 = PP_num
        pelco_d_pack.data1 = data_high
        pelco_d_pack.data2 = data_low
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def set_vert_preset_point(self, PP_num, data_high, data_low):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xe5
        pelco_d_pack.cmd2 = PP_num
        pelco_d_pack.data1 = data_high
        pelco_d_pack.data2 = data_low
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def set_preset_point_stoptime(self, PP_num, H_time, L_time):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf1
        pelco_d_pack.cmd2 = PP_num
        pelco_d_pack.data1 = H_time
        pelco_d_pack.data2 = L_time
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def set_preset_point_speed(self, PP_num, H_Speed, V_Speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf2
        pelco_d_pack.cmd2 = PP_num
        pelco_d_pack.data1 = H_Speed
        pelco_d_pack.data2 = V_Speed
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def preset_point_start(self, once, PP_num1, PP_num2):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf0
        if once == 1:               # 1 启动一次
            pelco_d_pack.cmd2 = 0x05
        else:                      # 0 启动且连续
            pelco_d_pack.cmd2 = 0x01
        pelco_d_pack.data1 = PP_num1
        pelco_d_pack.data2 = PP_num2
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def preset_point_pause_continue(self, pause):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf0
        if pause == 1:              # 1 停止
            pelco_d_pack.cmd2 = 0x02
        else:                      # 0 恢复
            pelco_d_pack.cmd2 = 0x03
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def preset_point_close(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xf0
        pelco_d_pack.cmd2 = 0x04
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)


    # 云台自定义0位

    # dir=1水平、=2垂直、=3水平和垂直；speed=1水平与垂直速度、=2水平速度、=3垂直速度；relay=1打开继电器，0关闭；action=1聚焦+、=0-
    # 视频设置基准0位，删除基准0位，云台复位重启，查询工作模式、状态，查询温度、工作电压、工作电流、速度，继电器开关（不建议使用:继电器被触发时使用），清除掉电位置数据，聚焦
    def auto_set_zero_posit(self, dir):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xe3
        if dir == 1:                 # 水平
            pelco_d_pack.cmd2 = 0x01
        elif dir == 2:               # 垂直
            pelco_d_pack.cmd2 = 0x02
        elif dir == 3:               # 水平和垂直
            pelco_d_pack.cmd2 = 0x03
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def del_zero_posit(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xe3
        pelco_d_pack.cmd2 = 0x06
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def reset_reboot(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xde
        pelco_d_pack.cmd2 = 0x00
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def work_mode(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xe0
        pelco_d_pack.cmd2 = 0x00
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def work_state(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xdd
        pelco_d_pack.cmd2 = 0x00
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def temp_inquire(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xd6
        pelco_d_pack.cmd2 = 0x00
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def volt_inquire(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xcd
        pelco_d_pack.cmd2 = 0x00
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def curr_inquire(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xc8
        pelco_d_pack.cmd2 = 0x00
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def speed_inquire(self, speed):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xd0
        if speed == 1:  # 水平与垂直速度
            pelco_d_pack.cmd2 = 0x00
        elif speed == 2:  # 水平速度
            pelco_d_pack.cmd2 = 0x01
        elif speed == 3:  # 垂直速度
            pelco_d_pack.cmd2 = 0x02
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def relay_control(self, relay):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xc0
        if relay == 1:  # 打开继电器
            pelco_d_pack.cmd2 = 0x01
        else:  # 关闭继电器（默认常关）
            pelco_d_pack.cmd2 = 0x00
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def clean_reset(self):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xbb
        pelco_d_pack.cmd2 = 0x01
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def adjust_focal(self, action):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        if action == 1:  # 1 聚焦+
            pelco_d_pack.cmd1 = 0x01
            pelco_d_pack.cmd2 = 0x00
        else:  # 0 聚焦-
            pelco_d_pack.cmd1 = 0x00
            pelco_d_pack.cmd2 = 0x80
        pelco_d_pack.data1 = 0x00
        pelco_d_pack.data2 = 0x00
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)



    # 自动回传

    # H_time：停止时间高8位、L_time：停止时间低8位
    # 温度、工作电压、工作电流、角度、速度实时回传
    def auto_return_temp(self, H_time, L_time):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xd4
        pelco_d_pack.cmd2 = 0x01
        pelco_d_pack.data1 = H_time
        pelco_d_pack.data2 = L_time
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def auto_return_volt(self, H_time, L_time):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xcc
        pelco_d_pack.cmd2 = 0x01
        pelco_d_pack.data1 = H_time
        pelco_d_pack.data2 = L_time
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def auto_return_curr(self, H_time, L_time):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xc1
        pelco_d_pack.cmd2 = 0x01
        pelco_d_pack.data1 = H_time
        pelco_d_pack.data2 = L_time
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def auto_return_angle(self, H_time, L_time):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xe1
        pelco_d_pack.cmd2 = 0x01
        pelco_d_pack.data1 = H_time
        pelco_d_pack.data2 = L_time
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)

    def auto_return_speed(self, H_time, L_time):
        pelco_d_pack = PelcoDProtocol()

        pelco_d_pack.addr = self.addr
        pelco_d_pack.cmd1 = 0xdc
        pelco_d_pack.cmd2 = 0x01
        pelco_d_pack.data1 = H_time
        pelco_d_pack.data2 = L_time
        pelco_d_pack.check = pelco_d_check(pelco_d_pack)

        # 通过以太网/485/422接口发送
        self.send_data(pelco_d_pack)
    def check_angle(self):
        a = self.process_respone_angel(self.get_level_angle())
        b = self.process_respone_angel(self.get_vertical_angle())
        print("level:",a,"vertical:",b)
class testangel:
    level_H = None
    level_L = None
def player():
    g1 = Gimbal()
    keyboard.add_hotkey("w",g1.turn_up,args=(0x10,))
    keyboard.add_hotkey("a",g1.turn_left,args=(0x10,))
    keyboard.add_hotkey("d",g1.turn_right,args=(0x10,))
    keyboard.add_hotkey("s",g1.turn_down,args=(0x10,))
    keyboard.add_hotkey("r",g1.turn_stop,args=())
    keyboard.add_hotkey("c",g1.check_angle,args=())
    while 1:
        key = keyboard.is_pressed("q")
        if key:
            return
#主函数
from time import sleep
if __name__ == '__main__':
    # 云台控制
    player()
    g1 = Gimbal()
    g1.get_level_angle()