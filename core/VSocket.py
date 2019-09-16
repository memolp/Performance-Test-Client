# -*- coding:utf-8 -*-

"""
  UDP的socket
"""

import socket

class VSocket:
    """
    user udp socket
    """
    def __init__(self, vuser, sockid, host, port):
        """
        创建socket
        :param vuser:
        :param sockid:
        :param host:
        :param port:
        """
        # 创建一个udp套接字
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__vuser = vuser
        self.__server = host
        self.__port  = port
        self.__sockid = sockid

    def OnReceive(self):
        """
        从压测中心接收到协议数据
        :return:
        """
        data, address = self.__sock.recvfrom(1024)
        self.__vuser.OnReceive(self.__sockid,data)

    def OnSend(self, buff):
        """
        发送数据给压测中心
        :param buff:
        :return:
        """
        try:
            self.__sock.sendto(buff,(self.__server,self.__port))
        except Exception as e:
            print(e)

    def GetFD(self):
        """
        获取socket
        :return:
        """
        return self.__sock