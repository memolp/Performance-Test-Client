# -*- coding:utf-8 -*-

"""
 压测用户
"""

from core.Packet import Packet
from core.VSocketMgr import VSocketMgr
from core.VTranslation import VTranslation


class VUser:
    """
    VUser 压测用户，无需业务层创建，底层创建后会将对象传递给业务层使用
    """
    MSG_CONNECT = 1000
    MSG_DISCONNECT = 1001
    MSG_PACKET = 2000

    def __init__(self, uid):
        """
        Create a Vuser by uid
        :param uid: uid 唯一标识
        """
        # 缓存存储数据
        self.__cacheCustomData = {}
        self.__uid = uid
        self.__task = None
        self.__socks = {}
        self.__states = {}
        self.__currentState = None
        self.__toState = None
        # 同一个事务可能存在多个统计，需要字典中用列表标识
        self.__translationList = {}
        self.__sendPacketIdx = 0
        self.__recvPacketIdx = 0
        self.__finishTranslation = []

    def SetData(self, key, data):
        """
        设置存储一些数据的接口
        :param key: 以key存储和读取 ，相同key会被覆盖
        :param data:
        :return:
        """
        self.__cacheCustomData[key] = data

    def GetData(self, key):
        """
        获取设置存储的数据
        :param key:
        :return:
        """
        return self.__cacheCustomData.get(key,None)

    def GetUID(self):
        """
        获取VUser的唯一标识UID
        :return:
        """
        return self.__uid

    def BindState(self, state, callback):
        """
        绑定一个状态事件，当状态改变时会调用回调方法
        :param state:
        :param callback:
        :return:
        """
        self.__states[state] = callback

    def SetState(self, state):
        """
        将状态设置为某个值，不触发回调
        :param state:
        :return:
        """
        self.__currentState = state

    def SwitchState(self, state):
        """
        状态状态，会生成一个回调，在合适的时机调用回调
        :param state:
        :return:
        """
        if state not in self.__states:
            raise KeyError("state :{0} is not exist!".format(state))
        # 状态在当前状态，不触发回调
        if state == self.__currentState:
            print("warning switchstate is in current state!")
            return
        # 如果状态已经是目标状态，则不执行
        if state == self.__toState:
            return
        self.__toState = state

    def GetStateCallback(self):
        """
        [private]获取状态回调方法，准备执行
        :return:
        """
        # 没有状态改变
        if self.__currentState == self.__toState:
            return None
        # 没有状态
        if self.__toState is None:
            return None
        # 更改状态
        self.__currentState = self.__toState
        # 返回状态回调函数
        return self.__states[self.__toState]

    def SetTask(self, task):
        """
        设置执行任务
        :param task:
        :return:
        """
        self.__task = task

    def TaskFinish(self):
        """
        返回任务是否完成
        :return:
        """
        if self.__task is None:
            return True
        return self.__task.done()

    def StartTranslation(self, mname):
        """
        创建一个事务，根据名称mname
        :param mname:
        :return:
        """
        if mname not in self.__translationList:
            self.__translationList[mname] = []
        translation = VTranslation(self, mname)
        # 添加事务到末尾
        self.__translationList[mname].append(translation)

    def EndTranslation(self, mname):
        """
        标记一个事务结束
        :param mname:
        :return:
        """
        if mname not in self.__translationList:
            raise KeyError("translation name :{0} is not exist!".format(mname))
        # 移除第一个事务标记完成
        translation = self.__translationList[mname].pop(0)
        translation.Finish()
        # 添加进完成事务列表
        self.__finishTranslation.append(translation)

    def Connect(self, host, port, sockid=0, socktype=0):
        """
        链接至指定的服务器地址，socket会存储到对应的sockid上
        :param host:
        :param port:
        :param sockid: 当前用户自己的sockid，用于指示一个user存在多个链接
        :param socktype: 创建链接的sock的类型 0 TCP 1 UDP
        :return:
        """
        self.__socks[sockid] = VSocketMgr.GetInstance().CreateVSocket(self, sockid)
        packet = self.CreatePacket(sockid, self.MSG_CONNECT)
        packet.writeUnsignedByte(socktype)
        packet.writeUnsignedShort(len(host))
        packet.writeUTFBytes(host)
        packet.writeUnsignedShort(port)
        self.Send(packet, sockid)

    def Send(self, packet, sockid=0):
        """
        向某个socketid 发送协议数据，如何socketid 不存在，会抛异常
        :param packet:
        :param sockid:
        :return:
        """
        if sockid not in self.__socks:
            raise KeyError("sockid :{0} is not exist!".format(sockid))
        packet.position = 1
        # 写入正确的协议长度 不包含起始标记和长度自己
        packet.writeUnsignedInt(packet.length()-5)
        self.__socks[sockid].OnSend(packet.getvalue())

    def CreatePacket(self, sockid=0, msgid=2000):
        """
        创建协议包
        :param sockid:
        :param msgid: 消息ID 正常无需设置此值
        :return: 返回一个Packet对象
        """
        packet = Packet()
        packet.writeUnsignedByte(0xEF)
        packet.writeUnsignedInt(0)
        packet.writeUnsignedInt(self.__uid)
        packet.writeUnsignedInt(self.__sendPacketIdx)
        packet.writeUnsignedShort(msgid)
        packet.writeUnsignedByte(sockid)
        self.__sendPacketIdx += 1
        return packet

    def OnReceive(self, sockid, data):
        """
        收到数据
        :param sockid:
        :param data:
        :return:
        """
        # 这里为什么会走VSocketMgr 主要是希望可以明确 这个返回是来自网络线程
        VSocketMgr.GetInstance().OnMessage(self, sockid, data)

    def OnClose(self, sockid):
        """
        服务器关闭
        :param sockid:
        :return:
        """
        VSocketMgr.OnDisconnect(self, sockid)
