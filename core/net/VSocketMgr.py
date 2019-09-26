# -*- coding:utf-8 -*-

"""
socket 管理器
"""

import time
import math
import selectors
import threading
import core.utils.VLog as VLog
import core.utils.VUtils as VUtils
import core.utils.threadpool as ThreadPool

from core.net.VSocket import VSocket



class VSocketMgr:
    """
    socket管理器
    """
    _instance = None
    MAX_SELECT_TASK_NUM = 4
    MAX_SELECT_NUM = 512
    RECV_MAX_BUFF_SIZE = 1024 * 1024
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
        self.__random = VUtils.Random()
        self.__executor = ThreadPool.ThreadExecutor(self.MAX_SELECT_TASK_NUM)

    def CreateServer(self, script, select_num):
        """
        创建server
        :param script:
        :param select_num: select数量
        :return:
        """
        self.__script = script
        # 创建指定数量的sock server
        for i in range(select_num):
            sel = VSelector()
            self.__serverList.append(sel)
            self.__executor.create(self._execute, sel)

    def CreateVSocket(self, vuser):
        """
        创建一个vsocket对象
        :param vuser:
        :param sockid:
        :return:
        """
        sock = VSocket(vuser, self.PTC_HOST, self.PTC_PORT , self.RECV_MAX_BUFF_SIZE)
        self.Register(sock)
        return sock

    def Register(self, sock):
        """
        注册socket
        :param sock:
        :return:
        """
        # 随机采样一个server 后面改为轮训方式吧-主要是针对win
        sockserver = self.__random.poll(self.__serverList, 1)
        if not sockserver:
            return
        # 注册
        sock.SetSocketServer(sockserver[0])
        sockserver[0].register(sock.GetFD(), selectors.EVENT_READ, sock.OnReceive)

    def _execute(self, selector):
        """
        select执行
        :param selector:
        :return:
        """
        try:
            selector.run()
        except Exception as e:
            VLog.Trace(e)


class VSelector:
    """ """
    def __init__(self):
        """ """
        self.__selector = selectors.DefaultSelector()

    def run(self):
        """"""
        try:
            events = self.__selector.select(0.001)
        except OSError:
            time.sleep(1.0)
            return
        except Exception as e:
            VLog.Trace(e)
            return
        for key, mask in events:
            func = key.data
            try:
                func()
            except Exception as e:
                VLog.Trace(e)

    def register(self, fileObj, mask, callback):
        """
        注册socket
        :param fileObj:
        :param mask:
        :param callback:
        :return:
        """
        self.__selector.register(fileObj, mask, callback)

    def remove(self,fileobj):
        """
        移除socket
        :param fileobj:
        :return:
        """
        self.__selector.unregister(fileobj)


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
            try:
                events = self.__selector.select(0.001)
            except OSError:
                time.sleep(1.0)
                continue
            except Exception as e:
                time.sleep(1.0)
                VLog.Trace(e)
                continue
            for key, mask in events:
                func = key.data
                try:
                    func()
                except Exception as e:
                    VLog.Trace(e)

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

    def remove(self,fileobj):
        """
        移除socket
        :param fileobj:
        :return:
        """
        self.__selector.unregister(fileobj)