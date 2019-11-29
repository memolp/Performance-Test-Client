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
    RPC Client 与 RPC服务进行通信
author:
    JeffXun
"""


import socket
import selectors
import threading


class RPCConnectType:
    """rpc 链接的服务器类型 """
    # RPC服务协议类型
    SOCK_TCP = 1
    SOCK_UDP = 2


class RPCClientBase(object):
    """
    RPC client base 接口类
    """

    def connect_rpc_server(self, host, port, connect_type=RPCConnectType.SOCK_TCP):
        """
        链接RPC服务器
        :param host: rpc 服务器ip地址
        :param port: rpc 服务器端口
        :param connect_type: 创建的链接类型 TPC or UDP
        :return:
        """
        return NotImplemented

    def send_to_server(self, msg_data):
        """
        向RPC服务器发送消息
        :param msg_data:  消息数据
        :return:
        """
        return NotImplemented


class RPCClient(RPCClientBase):
    """
     RPC client 定义交互的接口
    """
    def __init__(self):
        """
        构造
        """
        super(RPCClient, self).__init__()
        self.rpc_host = "127.0.0.1"
        self.rpc_port = -1
        self.connect_num = 1
        self.connect_type = RPCConnectType.SOCK_TCP
        self.selector = selectors.DefaultSelector()
        self.connect_sock = None
        self.recv_buff_size = -1
        self.send_buff_size = -1
        self.recv_from_size = 8192
        self.__running = False

    def set_recv_buff_size(self, buff_size):
        """
        设置接收数据缓存区大小
        :param buff_size:
        :return:
        """
        self.recv_buff_size = buff_size

    def set_send_buff_size(self, buff_size):
        """
        设置发送数据缓存区大小
        :param buff_size:
        :return:
        """
        self.send_buff_size = buff_size

    def set_recv_body_size(self, buff_size):
        """
        设置每次读取数据包的大小 注意如果UDP设置的读取值小于rpc服务器发送的包大小。数据包会丢或截断
        :param buff_size:
        :return:
        """
        self.recv_from_size = buff_size

    def connect_rpc_server(self, host, port, connect_type=RPCConnectType.SOCK_TCP):
        """
        连接rpc服务器
        :param host:
        :param port:
        :param connect_type:
        :return:
        """
        self.rpc_host = host
        self.rpc_port = port
        self.connect_type = connect_type
        self._create_connect()

    def _create_connect(self):
        """
        创建链接
        :return:
        """
        # 创建socket列表
        self.connect_sock = self._create_sock_type(self.connect_type)
        assert self.connect_sock is not None
        self.selector.register(self.connect_sock, selectors.EVENT_READ)
        # 启动线程
        self.__running = True
        self.__thread = threading.Thread(target=self._select_thread, args=())
        self.__thread.start()

    def _create_sock_type(self, sock_type):
        """
        创建socket
        :param sock_type:
        :return: socket object if create success
        """
        if sock_type == RPCConnectType.SOCK_TCP:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            sock.connect((self.rpc_host, self.rpc_port))
            # 取消设置非阻塞，否则sendall会报错
            # sock.setblocking(False)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 设置缓存buff
        if self.recv_buff_size > 0:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.recv_buff_size)
        if self.send_buff_size > 0:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.send_buff_size)
        return sock

    def _select_thread(self):
        """
        select thread
        :return:
        """
        while self.__running:
            events = self.selector.select()
            for key, mask in events:
                if mask & selectors.EVENT_READ:
                    self._sock_receive(key.fileobj)

    def _sock_tcp_receive(self, sock):
        """
        TCP socket 接收数据---处理粘包
        :param sock:
        :return:
        """
        return NotImplemented

    def _sock_udp_receive(self, sock):
        """
        udp socket 接收数据
        :param sock:
        :return:
        """
        return NotImplemented

    def _sock_receive(self, sock):
        """
        sock 读取数据
        :param sock:
        :return:
        """
        if self.connect_type == RPCConnectType.SOCK_TCP:
            self._sock_tcp_receive(sock)
        else:
            self._sock_udp_receive(sock)

    def send_to_server(self, msg_data):
        """
        发送数据
        :param msg_data:
        :return:
        """
        if self.connect_type == RPCConnectType.SOCK_TCP:
            self.connect_sock.sendall(msg_data)
        else:
            self.connect_sock.sendto(msg_data, (self.rpc_port, self.rpc_port))

    def close_connect(self):
        """
        断开rpc链接
        :return:
        """
        self.__running = False
        self.connect_sock.close()

