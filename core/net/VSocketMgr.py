# -*- coding:utf-8 -*-

"""
MIT License

Copyright (c) 2019 JeffXun

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

content:
    socket 管理器
author:
    JeffXun
"""

import time
import socket
import selectors
import threading

from core.utils.VLog import VLog
from core.utils.Packet import Packet


class VSocketMgr:
    """
    socket管理器
    """
    # RPC服务协议类型
    SOCK_TCP = 1
    SOCK_UDP = 2

    # RPC服务器地址
    PTC_HOST = "127.0.0.1"
    PTC_PORT = 7090

    # socket缓存区大小
    SOCK_BUFF_MAX_SIZE = 1024000
    # 单次读取数据大小
    SINGLE_RECV_BUFF_SIZE = 10240

    # 协议包头大小
    PACKET_HEAD_LEN = 20

    # 单例类
    _instance = None
    @staticmethod
    def GetInstance():
        """
        单例
        :return:
        """
        if VSocketMgr._instance is None:
            VSocketMgr._instance = VSocketMgr()
        return VSocketMgr._instance

    def __init__(self):
        """"""
        self.__selector = selectors.DefaultSelector()
        self.__running = False
        self.__thread = None
        self.__sock_list = []
        self.__sock_num = 0
        self.__sock_type = 0
        self.__cache_packet = {}
        self.__userDict = {}

    def _select_thread(self):
        """
        select thread
        :return:
        """
        while self.__running:
            events = self.__selector.select()
            for key, mask in events:
                if mask & selectors.EVENT_READ:
                    self._sock_recevie(key.fileobj)

    def _sock_tcp_recevie(self, sock):
        """
        TCP socket 接收数据---处理粘包
        :param sock:
        :return:
        """
        begin_time = 0
        if VLog.Performance_Log:
            begin_time = time.time() * 1000

        try:
            data = sock.recv(self.SINGLE_RECV_BUFF_SIZE)
        except Exception as e:
            VLog.Trace(e)
            return

        if sock not in self.__cache_packet:
            self.__cache_packet[sock] = Packet()

        # 缓存包
        cache_packet = self.__cache_packet[sock]
        cache_packet.position = cache_packet.length()
        cache_packet.writeMulitBytes(data)
        cache_packet.position = 0
        length = cache_packet.length()

        # 这里的分包只是分底层组装的包，具体服务器返回的协议内容有没有完整，需要OnMessage中自己判断
        while length - cache_packet.position > 0:
            # 长度不足
            if length - cache_packet.position < self.PACKET_HEAD_LEN:
                break
            # 开始标记不对
            head_flag = cache_packet.readUnsignedByte()
            if head_flag != 0xEF:
                cache_packet.clear()
                VLog.Error("[PTC] Recv Packet Head ERROR! flag:{0}", head_flag)
                break
            pack_len = cache_packet.readUnsignedInt()
            # 协议长度不足
            if length - cache_packet.position < pack_len:
                cache_packet.position = length
                break
            # 检查uid
            uid = cache_packet.readUnsignedInt()
            # 读取完整的协议包
            completed_packet = Packet(cache_packet.readMulitBytes(pack_len - 4))
            self._msg_pack(uid, completed_packet)
            # 读取剩余内容
            remaining = length - cache_packet.position
            if remaining <= 0:
                cache_packet.clear()
            else:
                cdata = cache_packet.readMulitBytes(remaining)
                cache_packet.reset(cdata)
            length = cache_packet.length()

        if VLog.Performance_Log:
            cost_time = time.time() * 1000 - begin_time
            if cost_time > 20:
                VLog.Fatal("[PERFORMANCE] OnReceice Cost Time:{0}ms UID:{1}", cost_time)

        # 最后删除数据
        del data

    def _sock_udp_recevie(self, sock):
        """
        udp socket 接收数据
        :param sock:
        :return:
        """
        begin_time = 0
        if VLog.Performance_Log:
            begin_time = time.time() * 1000

        try:
            # 单个协议包的大小，必须与发送方使用一致，否则会丢包
            buff, address = sock.recvfrom(self.SINGLE_RECV_BUFF_SIZE)
        except Exception as e:
            VLog.Trace(e)
            return

        # 检查协议头和长度是否正确
        packet = Packet(buff)

        #
        del buff

        head_flag = packet.readUnsignedByte() & 0xFF
        if head_flag != 0xEF:
            VLog.Error("[PTC] Recv Packet Head ERROR! flag:{0}", head_flag)
            return
        pack_len = packet.readUnsignedInt()
        if packet.length() - packet.position < pack_len:
            VLog.Error("[PTC] Recv Packet Size ERROR! size:{0} ",pack_len)
            return

        # udp 协议不会粘包，直接发送即可
        uid = packet.readUnsignedInt()
        self._msg_pack(uid, packet)

        if VLog.Performance_Log:
            cost_time = time.time() * 1000 - begin_time
            if cost_time > 20:
                VLog.Fatal("[PERFORMANCE] OnReceice Cost Time:{0}ms UID:{1}", cost_time)

    def _msg_pack(self, uid, packet):
        """
        消息协议
        :param uid:
        :param packet:
        :return:
        """
        vuser = self.__userDict.get(uid)
        if not vuser:
            return
        try:
            vuser.OnMessage(packet)
            del packet
        except Exception as e:
            VLog.Trace(e)

    def _sock_recevie(self, sock):
        """
        sock 读取数据
        :param sock:
        :return:
        """
        if self.__sock_type == self.SOCK_TCP:
            self._sock_tcp_recevie(sock)
        else:
            self._sock_udp_recevie(sock)

    def CreateServer(self, sock_num, sock_type):
        """
        创建server
        :param sock_num:
        :param sock_type:
        :return:
        """
        self.Clear()
        self.__sock_num = sock_num
        self.__sock_type = sock_type
        # 创建socket列表
        for i in range(sock_num):
            s = self._create_sock_type(sock_type)
            self.__selector.register(s, selectors.EVENT_READ)
            self.__sock_list.append(s)
        # 启动线程
        self.__running = True
        self.__thread = threading.Thread(target=self._select_thread, args=())
        self.__thread.start()

    def _create_sock_type(self, sock_type):
        """
        创建socket
        :param sock_type:
        :return:
        """
        sock = None
        if sock_type == self.SOCK_TCP:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.SOCK_BUFF_MAX_SIZE)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.SOCK_BUFF_MAX_SIZE)
            sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            sock.connect((self.PTC_HOST, self.PTC_PORT))
            sock.setblocking(False)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.SOCK_BUFF_MAX_SIZE)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.SOCK_BUFF_MAX_SIZE)
        return sock

    def SendPacket(self, uid, bin_data):
        """
        发送数据包
        :param uid: 多个socket的时候，根据uid去模指定的socket
        :param bin_data:
        :return:
        """
        index = int(uid % self.__sock_num)
        sock = self.__sock_list[index]
        if not sock:
            VLog.Error("Send packet with none socket")
        if self.__sock_type == self.SOCK_TCP:
            sock.sendall(bin_data)
        else:
            sock.sendto(bin_data, (self.PTC_HOST, self.PTC_PORT))

    def Register(self, uid , user):
        """
        vuser 将自己注册进来，以便可以接受消息
        :param uid:
        :param user:
        :return:
        """
        self.__userDict[uid] = user

    def UnRegister(self, uid):
        """
        反注册
        :param uid:
        :return:
        """
        if uid in self.__userDict:
            del self.__userDict[uid]

    def Stop(self):
        """
        停止
        :return:
        """
        self.__running = False

    def Clear(self):
        """
        清理
        :return:
        """
        self.__userDict.clear()
        self.__userDict = {}