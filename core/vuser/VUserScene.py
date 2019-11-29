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
    压测场景基础类，其他的场景需要继承此类
author:
    JeffXun
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

    def OnMessage(self, sock_id, packet, timestamp=0):
        """
        网络收包返回
        :param sock_id:
        :param packet: 二进制协议内容
        :param timestamp: 协议包自带的时间戳 0表示没有
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
