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
    压测用户
author:
    JeffXun
"""
import time
import queue

import core.utils.VUtils as VUtils

from core.utils.VLog import VLog
from core.utils.Packet import Packet
from core.utils.threadpool import SingletonThreadExecutor
from core.net.VSocketMgr import VSocketMgr
from core.utils.VTranslation import VTranslation
from core.vuser.VUserScene import VUserScene


class VUser(object):
    """
    VUser 压测用户，无需业务层创建，底层创建后会将对象传递给业务层使用
    """
    MSG_CONNECT = 1000
    MSG_DISCONNECT = 1001
    MSG_PACKET = 2000
    PACKET_HEAD_LEN = 20

    def __init__(self, uid):
        """
        Create a Vuser by uid
        :param uid: uid 唯一标识
        """
        # 缓存存储数据
        self.__cacheCustomData = {}
        self.__uid = uid
        self.__scene = None
        self.__task = None
        self.__states = {}
        self.__currentState = None
        self.__initCompleted = False
        self.__useBusy = True
        self.__stateCallArgs = []
        self.__toState = None
        # 同一个事务可能存在多个统计，需要字典中用列表标识
        self.__translationList = {}
        self.__tickCalback = None
        self.__finishTranslation = {}
        VSocketMgr.GetInstance().Register(uid, self)


    def ClearData(self):
        """
        清理數據
        :return:
        """
        # 缓存存储数据
        self.__cacheCustomData = {}
        self.__scene = None
        self.__task = None
        self.__states = {}
        self.__currentState = None
        self.__initCompleted = False
        self.__useBusy = True
        self.__stateCallArgs = []
        self.__toState = None
        self.__tickCalback = None

    def GetScene(self):
        """
        获取场景对象
        :return:
        """
        return self.__scene

    def SetScene(self, scene):
        """
        设置压测场景
        :param scene:
        :return:
        """
        if isinstance(scene, VUserScene):
            VLog.Debug("VUser {0} Change Scene {1}", self.__uid, scene.sceneName)
            self.ClearData()
            self.__scene = scene

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

    def GetHashCode(self,value):
        """
        获取value的hashcode
        :param value:
        :return:
        """
        return abs(VUtils.GetHashCode(value))

    def GetStateLabel(self):
        """
        获取当前user的状态
        :return:
        """
        if not self.__initCompleted:
            return "Init"
        if self.__useBusy:
            return "running"
        return "wait"

    def GetInitCompleted(self):
        """
        返回初始化完成
        :return:
        """
        return self.__initCompleted

    def SetInitCompleted(self, value):
        """
        设置初始化完成标记
        :param value:
        :return:
        """
        self.__initCompleted = value

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

    def SwitchState(self, state, *args):
        """
        状态状态，会生成一个回调，在合适的时机调用回调
        :param state:
        :return:
        """
        if state not in self.__states:
            VLog.Error("[PTC] state :{0} is not exist! uid:{1}", state, self.__uid)
            return
        # 状态在当前状态，不触发回调
        if state == self.__currentState:
            VLog.Info("[PTC] warning switchstate is in current state :{0} uid: {1}!", state, self.__uid)
            return
        # 如果状态已经是目标状态，则不执行
        if state == self.__toState:
            return
        self.__toState = state
        self.__stateCallArgs = args

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

    def GetStateCallbackArgs(self):
        """
        获取状态改变回调的传入参数
        :return:
        """
        return self.__stateCallArgs

    def GetTickCallback(self):
        """
        [private]获取定时回调方法
        :return:
        """
        return self.__tickCalback

    def SetTickCallback(self,callback):
        """
        设置定时回调方法 1秒间隔
        :param callback:
        :return:
        """
        self.__tickCalback = callback

    def GetState(self):
        """
        获取当前的状态
        :return:
        """
        return self.__currentState

    def IsFinished(self):
        """
        返回任务是否完成
        :return:
        """
        if self.__useBusy:
            return False
        return True

    def SetBusy(self, bool):
        """
        这是用户繁忙状态
        :param bool:
        :return:
        """
        self.__useBusy = bool

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
            VLog.Error("[PTC] uid:{0} translation name :{1} is not exist!", self.__uid, mname)
            return
        # 移除第一个事务标记完成
        if len(self.__translationList[mname]) > 0:
            translation = self.__translationList[mname].pop(0)
            translation.Finish()
            # 添加进完成事务列表
            if mname not in self.__finishTranslation:
                self.__finishTranslation[mname] = []
            self.__finishTranslation[mname].append(translation)

    def GetTranslationInfo(self):
        """
        获取事务信息
        :return: 进行中事务列表，已完成事务列表
        """
        return self.__translationList, self.__finishTranslation

    def Connect(self, host, port, sockid, socktype=0):
        """
        链接至指定的服务器地址，socket会存储到对应的sockid上
        :param host:
        :param port:
        :param sockid: 当前用户自己的sockid，用于指示一个user存在多个链接
        :param socktype: 创建链接的sock的类型 0 TCP 1 UDP
        :return:
        """
        # 先清除数据，这个也是坑
        #self.__cachePacketData.clear()
        packet = self.CreatePacket()
        packet.writeUnsignedByte(socktype)
        packet.writeUnsignedShort(len(host))
        packet.writeUTFBytes(host)
        packet.writeUnsignedShort(port)
        self.__SendPacket(packet, sockid, self.MSG_CONNECT)

    def Disconnect(self, sockid, broadcast=False):
        """
        主动断开链接
        :param sockid:
        :param broadcast: 是否通知服务器
        :return:
        """
        # 默认不通知服务器
        if broadcast:
            packet = self.CreatePacket()
            self.__SendPacket(packet, sockid, self.MSG_DISCONNECT)


    def __SendPacket(self, packet, sockid , msgid):
        """
        向某个socketid 发送协议
        :param packet:
        :param sockid:
        :param msgid:
        :return:
        """
        start_time = time.time() * 1000
        # 发送的数据需要再重新包装
        sendPacket = Packet()
        # 起始标记
        sendPacket.writeUnsignedByte(0xEF)
        # 协议长度-预先站位
        sendPacket.writeUnsignedInt(0)
        # 用户vuer
        sendPacket.writeUnsignedInt(self.__uid)
        # 发送的序列号
        sendPacket.writeInt64(int(time.time()*1000))
        # sockid
        sendPacket.writeUnsignedByte(sockid)
        # 消息ID
        sendPacket.writeUnsignedShort(msgid)
        # 内容
        sendPacket.writeUTFBytes(packet.getvalue())
        # 更新长度
        sendPacket.position = 1
        # 写入正确的协议长度 不包含起始标记和长度自己
        sendPacket.writeUnsignedInt(sendPacket.length()-5)
        packet_time = time.time() * 1000 - start_time
        # 发送数据
        VSocketMgr.GetInstance().SendPacket(self.__uid, sendPacket.getvalue())
        send_time = time.time() * 1000 - start_time
        if send_time > 10 or packet_time > 10:
            VLog.Warning("Send Pack time packtime{0} ms , sendtime{1} ms", packet_time, send_time)
        # 清除
        del packet
        del sendPacket


    def Send(self, packet, sockid):
        """
        向某个socketid 发送协议数据
        :param packet:
        :param sockid:
        :return:
        """
        # 发送数据
        self.__SendPacket(packet, sockid, self.MSG_PACKET)

    def CreatePacket(self,data=None):
        """
        创建协议包
        :return: 返回一个Packet对象
        """
        return Packet(data)

    def OnMessage(self, packet):
        """
        消息包
        :param packet:
        :return:
        """
        current = time.time()
        # 检查序号
        timestamp = packet.readUnsignedInt64()
        if current - timestamp > 10:
           VLog.Warning("[PTC] Deal Packet time is cost")
        sock_id = packet.readUnsignedByte()
        msg_id = packet.readUnsignedShort()
        if msg_id == self.MSG_DISCONNECT:
            self.__OnClose(sock_id)
        elif msg_id == self.MSG_PACKET:
            buff_data = packet.readMulitBytes(packet.length() - packet.position)
            self.__OnMessage(sock_id, buff_data)
        elif msg_id == self.MSG_CONNECT:
            self.__OnConnected(sock_id)
        else:
            VLog.Error("[PTC] Recv Packet MsgID ERROR! msg:{0} ", msg_id)

    def __OnClose(self, sock_id):
        """
        服务器关闭
        :param sock_id:
        :return:
        """
        VLog.Debug("[PTC] Server Closed the socket uid:{0} , sockID:{1}", self.__uid, sock_id)
        try:
            self.__scene.OnDisconnect(sock_id)
        except Exception as e:
            VLog.Trace(e)
        self.Disconnect(sock_id, False)

    def __OnConnected(self, sock_id):
        """
        服务器链接成功
        :param sock_id:
        :return:
        """
        VLog.Debug("[PTC] Server connected the socket uid:{0} , sockID:{1}", self.__uid, sock_id)
        try:
            self.__scene.OnConnected(sock_id)
        except Exception as e:
            VLog.Trace(e)

    def __OnMessage(self, sock_id, packet):
        """
        协议返回
        :param sock_id:
        :param packet:
        :return:
        """
        try:
            self.__scene.OnMessage(sock_id, packet)
        except Exception as e:
            VLog.Trace(e)
