# -*-coding:utf-8 -*-

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
    VUser 压测用户使用的RPC对象
author:
    JeffXun
"""

import time


from core.utils.VLog import VLog
from core.utils.Packet import Packet
from core.rpc.RPCClient import RPCClient


class PTCRPCClient(RPCClient):
    """
    PTC rpc client
    """
    def __init__(self):
        """
        构造
        """
        super(PTCRPCClient, self).__init__()
        self.user_callback = {}
        self.pack_head_len = 20
        self.cache_packet = Packet()

    def register_user(self, uid, callback):
        """
        注册用户callback
        :param uid:
        :param callback:
        :return:
        """
        self.user_callback[uid] = callback

    def _sock_tcp_receive(self, sock):
        """
        TCP socket 接收数据---处理粘包
        :param sock:
        :return:
        """
        begin_time = 0
        if VLog.PROFILE_OPEN:
            begin_time = time.time() * 1000

        try:
            data = sock.recv(self.recv_from_size)
        except Exception as e:
            VLog.Trace(e)
            return

        # 缓存包
        self.cache_packet.position = self.cache_packet.length()
        self.cache_packet.writeMulitBytes(data)
        self.cache_packet.position = 0
        length = self.cache_packet.length()

        # 这里的分包只是分底层组装的包，具体服务器返回的协议内容有没有完整，需要OnMessage中自己判断
        while length - self.cache_packet.position > 0:
            # 长度不足
            if length - self.cache_packet.position < self.pack_head_len:
                break
            # 开始标记不对
            head_flag = self.cache_packet.readUnsignedByte()
            if head_flag != 0xEF:
                self.cache_packet.clear()
                VLog.Error("[PTC] Recv Packet Head ERROR! flag:{0}", head_flag)
                break
            pack_len = self.cache_packet.readUnsignedInt()
            # 协议长度不足
            if length - self.cache_packet.position < pack_len:
                self.cache_packet.position = length
                break
            # 检查uid
            uid = self.cache_packet.readUnsignedInt()
            # 读取完整的协议包
            completed_packet = Packet(self.cache_packet.readMulitBytes(pack_len - 4))
            self._msg_pack(uid, completed_packet)
            # 读取剩余内容
            remaining = length - self.cache_packet.position
            if remaining <= 0:
                self.cache_packet.clear()
            else:
                cdata = self.cache_packet.readMulitBytes(remaining)
                self.cache_packet.reset(cdata)
            length = self.cache_packet.length()

        if VLog.PROFILE_OPEN:
            cost_time = time.time() * 1000 - begin_time
            if cost_time > 20:
                VLog.Profile("TCP Packet receive cost {0}ms", cost_time)

        # 最后删除数据
        del data

    def _sock_udp_receive(self, sock):
        """
        udp socket 接收数据
        :param sock:
        :return:
        """
        begin_time = 0
        if VLog.PROFILE_OPEN:
            begin_time = time.time() * 1000

        try:
            # 单个协议包的大小，必须与发送方使用一致，否则会丢包
            buff, address = sock.recvfrom(self.recv_from_size)
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
            VLog.Error("[PTC] Recv Packet Size ERROR! size:{0} ", pack_len)
            return

        # udp 协议不会粘包，直接发送即可
        uid = packet.readUnsignedInt()
        self._msg_pack(uid, packet)

        if VLog.PROFILE_OPEN:
            cost_time = time.time() * 1000 - begin_time
            if cost_time > 20:
                VLog.Profile("UDP Packet receive cost {0}ms ", cost_time)

    def _msg_pack(self, uid, packet):
        """
        消息协议
        :param uid:
        :param packet:
        :return:
        """
        callback = self.user_callback.get(uid)
        if not callback:
            return
        try:
            callback(packet)
            del packet
        except Exception as e:
            VLog.Trace(e)
