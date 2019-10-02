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
    UDP的socket
author:
    JeffXun
"""

import socket
import core.utils.VLog as VLog


class VSocket:
    """
    user udp socket
    """
    def __init__(self, vuser, host, port , maxbufszie):
        """
        创建socket
        :param vuser:
        :param host:
        :param port:
        """
        # 创建一个udp套接字
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,maxbufszie)
        self.__sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,maxbufszie)
        self.__vuser = vuser
        self.__server = host
        self.__port  = port
        self.__selectServer = None
        self.__maxbufszie = maxbufszie

    def SetSocketServer(self,_server):
        """
        保存对线程server的引用
        :param _server:
        :return:
        """
        self.__selectServer = _server

    def OnReceive(self):
        """
        从压测中心接收到协议数据
        :return:
        """
        try:
            data, address = self.__sock.recvfrom(self.__maxbufszie)
        except ConnectionResetError:
            self.Close()
            return
        except Exception as e:
            VLog.Trace(e)
            self.Close()
            return
        try:
            self.__vuser.OnReceive(data)
        except Exception as e:
            VLog.Trace(e)

    def OnSend(self, buff):
        """
        发送数据给压测中心
        :param buff:
        :return:
        """
        try:
            self.__sock.sendto(buff,(self.__server,self.__port))
        except Exception as e:
            VLog.Trace(e)

    def GetFD(self):
        """
        获取socket
        :return:
        """
        return self.__sock

    def Close(self):
        """
        关闭套接字
        :return:
        """
        if self.__selectServer is not None:
            self.__selectServer.remove(self.__sock)