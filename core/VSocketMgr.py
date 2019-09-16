# -*- coding:utf-8 -*-

"""
socket 管理器
"""

import time
import selectors
import threading
import random

from core.VSocket import VSocket


class VSocketMgr:
    """
    socket管理器
    """
    _instance = None
    WIN_MAX_THREAD_NUM = 4
    PTC_HOST = "127.0.0.1"
    PTC_PORT = 7090
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
        self.__serverList = []
        self.__script = None

    def CreateServer(self,script, platform="win"):
        """
        创建server
        :param script:
        :param platform:
        :return:
        """
        self.__script = script
        if platform == "win":
            # 创建指定数量的sock server
            for i in range(self.WIN_MAX_THREAD_NUM):
                self.__serverList.append(_VSocketServerThread())
                self.__serverList[-1].start()
        elif platform == "linux":
            # epoll只需一个线程即可
            self.__serverList.append(_VSocketServerThread())
            self.__serverList[-1].start()
        else:
            raise TypeError("platform :{0} is not support!".format(platform))

    def CreateVSocket(self, vuser, sockid):
        """
        创建一个vsocket对象
        :param vuser:
        :param sockid:
        :return:
        """
        sock = VSocket(vuser, sockid, self.PTC_HOST, self.PTC_PORT)
        self.Register(sock)
        return sock

    def Register(self, sock):
        """
        注册socket
        :param sock:
        :return:
        """
        # 随机采样一个server 后面改为轮训方式吧-主要是针对win
        sockserver = random.sample(self.__serverList,1)
        if not sockserver:
            return
        # 注册
        sockserver[0].register(sock.GetFD(), selectors.EVENT_READ, sock.OnReceive)

    def OnMessage(self, vuser, sockid, data):
        """
        某个user网络协议返回
        :param vuser:
        :param sockid:
        :param data:
        :return:
        """
        try:
            self.__script.OnMessage(vuser, sockid, data)
        except Exception as e:
            print(e)

    # 网络链接断开
    def OnDisconnect(self, vuser, sockid):
        """
        某个user的网络断开
        :param vuser:
        :param sockid:
        :return:
        """
        try:
            self.__script.OnDisconnect(vuser, sockid)
        except Exception as e:
            print(e)

class _VSocketServerThread(threading.Thread):
    """
    socket线程，避免socket过多导致select无法满足的问题
    """
    def __init__(self):
        """"""
        threading.Thread.__init__(self)
        self.__selector = selectors.DefaultSelector()
        self.__registered = False

    def run(self):
        """"""
        while True:
            if not self.__registered:
                time.sleep(1.0)
                continue
            events = self.__selector.select()
            for key, mask in events:
                func = key.data
                try:
                    func()
                except Exception as e:
                    print(e)

    def register(self, fileObj, mask, callback):
        """
        注册socket
        :param fileObj:
        :param mask:
        :param callback:
        :return:
        """
        self.__selector.register(fileObj, mask, callback)
        self.__registered = True