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
from core.vuser.VUserMgr import VUserMgr
import core.utils.VUtils as VUtils


class VSocketMgr:
    """
    socket管理器
    """
    SOCK_TCP = 1
    SOCK_UDP = 2
    _instance = None
    MAX_SELECT_TASK_NUM = 4
    RECV_MAX_BUFF_SIZE = 1024000
    PTC_HOST = "127.0.0.1"
    PTC_PORT = 7090
    PACKET_HEAD_LEN = 20
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
        self.__socklist = Sockets()
        self.__sock_type = 0
        self.__cachePacketData = Packet()

    def _select_thread(self):
        """
        select thread
        :return:
        """
        while self.__running:
            events = self.__selector.select()
            for key, mask in events:
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
            data = sock.recv(self.RECV_MAX_BUFF_SIZE)
        except Exception as e:
            VLog.Trace(e)
            return

        self.__cachePacketData.position = self.__cachePacketData.length()
        self.__cachePacketData.writeMulitBytes(data)
        self.__cachePacketData.position = 0
        length = self.__cachePacketData.length()
        # 这里的分包只是分底层组装的包，具体服务器返回的协议内容有没有完整，需要OnMessage中自己判断
        while length - self.__cachePacketData.position > 0:
            # 长度不足
            if length - self.__cachePacketData.position < self.PACKET_HEAD_LEN:
                break
            # 开始标记不对
            head_flag = self.__cachePacketData.readUnsignedByte() & 0xFF
            if head_flag != 0xEF:
                self.__cachePacketData.clear()
                VLog.Error("[PTC] Recv Packet Head ERROR! flag:{0}", head_flag)
                break
            pack_len = self.__cachePacketData.readUnsignedInt()
            # 协议长度不足
            if length - self.__cachePacketData.position < pack_len:
                self.__cachePacketData.position = length
                break
            # 检查uid
            uid = self.__cachePacketData.readUnsignedInt()
            # 检查序号
            timestamp = self.__cachePacketData.readUnsignedInt64()
            sock_id = self.__cachePacketData.readUnsignedByte()
            msg_id = self.__cachePacketData.readUnsignedShort()
            user = VUserMgr.GetInstance().GetUserByUID(uid)
            if not user:
                break
            if msg_id == self.MSG_DISCONNECT:
                user.__OnClose(sock_id)
            elif msg_id == self.MSG_PACKET:
                rdata = self.__cachePacketData.readMulitBytes(pack_len - (self.PACKET_HEAD_LEN - 5))
                user.__OnMessage(sock_id, Packet(rdata))
            elif msg_id == self.MSG_CONNECT:
                user.__OnConnected(sock_id)
            else:
                VLog.Error("[PTC] Recv Packet MsgID ERROR! msg:{0} ", msg_id)
            # 读取剩余内容
            remaining = length - self.__cachePacketData.position
            if remaining <= 0:
                self.__cachePacketData.clear()
            else:
                cdata = self.__cachePacketData.readMulitBytes(remaining)
                self.__cachePacketData.reset(cdata)
            length = self.__cachePacketData.length()
        if VLog.Performance_Log:
            cost_time = time.time() * 1000 - begin_time
            if cost_time > 20:
                VLog.Fatal("[PERFORMANCE] OnReceice Cost Time:{0}ms UID:{1}", cost_time)


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
            buff, address = sock.recvform(self.RECV_MAX_BUFF_SIZE)
        except Exception as e:
            VLog.Trace(e)
            return

        packet = Packet(buff)
        head_flag = packet.readUnsignedByte() & 0xFF
        if head_flag != 0xEF:
            VLog.Error("[PTC] Recv Packet Head ERROR! flag:{0}", head_flag)
            return
        pack_len = packet.readUnsignedInt()
        if packet.length() - packet.position < pack_len:
            VLog.Error("[PTC] Recv Packet Size ERROR! size:{0} ",pack_len)
            return
        # 检查uid
        uid = packet.readUnsignedInt()
        # 检查序号
        timestamp = packet.readUnsignedInt64()
        sock_id = packet.readUnsignedByte()
        msg_id = packet.readUnsignedShort()
        user = VUserMgr.GetInstance().GetUserByUID(uid)
        if not user:
            return
        if msg_id == self.MSG_DISCONNECT:
            user.__OnClose(sock_id)
        elif msg_id == self.MSG_PACKET:
            rdata = packet.readMulitBytes(pack_len - (self.PACKET_HEAD_LEN - 5))
            user.__OnMessage(sock_id, Packet(rdata))
        elif msg_id == self.MSG_CONNECT:
            user.__OnConnected(sock_id)
        else:
            VLog.Error("[PTC] Recv Packet MsgID ERROR! msg:{0} ", msg_id)

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
        self.__sock_type = sock_type
        # 创建socket列表
        for i in range(sock_num):
            s = self._create_sock_type(sock_type)
            self.__selector.register(s, selectors.EVENT_READ)
            self.__socklist.append(s)
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
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.RECV_MAX_BUFF_SIZE)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.RECV_MAX_BUFF_SIZE)
            sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            sock.connect((self.PTC_HOST, self.PTC_PORT))
            sock.setblocking(False)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.RECV_MAX_BUFF_SIZE)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.RECV_MAX_BUFF_SIZE)
        return sock

    def SendPacket(self, bin_data):
        """
        发送数据包
        :param bin_data:
        :return:
        """
        sock = self.__socklist.poll()
        if not sock:
            VLog.Error("Send packet with none socket")
        if self.__sock_type == self.SOCK_TCP:
            sock.sendall(bin_data)
        else:
            sock.sendto(bin_data, (self.PTC_HOST, self.PTC_PORT))

    def Stop(self):
        """
        停止
        :return:
        """
        self.__running = False


class Sockets(list):
    def __init__(self):
        """"""
        super(Sockets, self).__init__()
        self.random = VUtils.Random()

    def poll(self):
        return self.random.poll(self, 1)