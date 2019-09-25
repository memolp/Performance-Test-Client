# -*- coding:utf-8 -*-

"""
    压测场景基础类，其他的场景需要继承此类
"""

class VUserScene(object):
    """
      压测基础类
    """
    def __init__(self, vuser, name):
        """
        创建压测场景对象，需要传入vuser和场景名
        :param vuser: 用户对象
        :param name: 场景名
        """
        self.vUser = vuser
        self.sceneName = name

    def OnMessage(self, sock_id, packet):
        """
        网络收包返回
        :param sock_id:
        :param packet:
        :return:
        """
        raise NotImplementedError("Must implemented this method!")

    def OnConcurrence(self, count):
        """
        并发执行调用
        :param count:
        :return:
        """
        raise NotImplementedError("Must implemented this method!")

    def OnInit(self):
        """
        vuser创建后调用
        :return:
        """
        raise NotImplementedError("Must implemented this method!")

    def OnDisconnect(self, sock_id):
        """
        网络链接断开调用
        :param sock_id:
        :return:
        """
        return NotImplemented

    def OnConnected(self, sock_id):
        """
        网络链接完成
        :param sock_id:
        :return:
        """
        return NotImplemented
