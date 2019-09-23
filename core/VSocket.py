# -*- coding:utf-8 -*-

"""
  UDP的socket
"""

import socket
import core.VLog as VLog


class VSocket:
    """
    user udp socket
    """
    def __init__(self, vuser, sockid, host, port , maxbufszie):
        """
        创建socket
        :param vuser:
        :param sockid:
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
        self.__sockid = sockid
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
        except Exception as e:
            VLog.Trace(e)
            self.Close()
            return
        try:
            self.__vuser.OnReceive(self.__sockid,data)
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