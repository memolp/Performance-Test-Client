# -*- coding:utf-8 -*-

"""
 压测用户
"""
import time
import core.VLog as VLog
import core.VUtils as VUtils

from core.Packet import Packet
from core.VSocketMgr import VSocketMgr
from core.VTranslation import VTranslation


class VUser(object):
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
        self.__initCompleted = False
        self.__useBusy = True
        self.__stateCallArgs = []
        self.__toState = None
        # 同一个事务可能存在多个统计，需要字典中用列表标识
        self.__translationList = {}
        # 缓存发送的序列号 按照sockid存储，互不影响
        self.__cachePacketIndex = {}
        self.__tickCalback = None
        self.__finishTranslation = {}
        # [底层的]缓存未读取完的数据包
        self.__cachePacketData = Packet()

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
        if self.__useBusy:
            return False
        if self.__task is None:
            return True
        return self.__task.done()

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
        self.__cachePacketData.clear()
        self.__cachePacketIndex[sockid] = {"SendIdx": 0, "ReceiveIdx": 0}
        self.__socks[sockid] = VSocketMgr.GetInstance().CreateVSocket(self, sockid)
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
        if sockid not in self.__socks:
            VLog.Error("[PTC] uid:{0} sockid :{1} is not exist!", self.__uid, sockid)
            return
        # 默认不通知服务器
        if broadcast:
            packet = self.CreatePacket()
            self.__SendPacket(packet, sockid, self.MSG_DISCONNECT)
        self.__socks[sockid].Close()
        del self.__socks[sockid]


    def __SendPacket(self, packet, sockid , msgid):
        """
        向某个socketid 发送协议
        :param packet:
        :param sockid:
        :param msgid:
        :return:
        """
        if sockid not in self.__socks:
            VLog.Error("[PTC] uid:{0} sockid :{1} is not exist!", self.__uid, sockid)
            return
        # 发送的数据需要再重新包装
        sendPacket = Packet()
        # 起始标记
        sendPacket.writeUnsignedByte(0xEF)
        # 协议长度-预先站位
        sendPacket.writeUnsignedInt(0)
        # 用户vuer
        sendPacket.writeUnsignedInt(self.__uid)
        # 发送的序列号
        index = self.__cachePacketIndex[sockid]["SendIdx"]
        sendPacket.writeUnsignedInt(index)
        self.__cachePacketIndex[sockid]["SendIdx"] += 1
        # 消息ID
        sendPacket.writeUnsignedShort(msgid)
        # sockid
        sendPacket.writeUnsignedByte(sockid)
        # 内容
        sendPacket.writeUTFBytes(packet.getvalue())
        # 更新长度
        sendPacket.position = 1
        # 写入正确的协议长度 不包含起始标记和长度自己
        sendPacket.writeUnsignedInt(sendPacket.length()-5)
        # 发送数据
        self.__socks[sockid].OnSend(sendPacket.getvalue())
        # 清除
        del packet
        del sendPacket


    def Send(self, packet, sockid):
        """
        向某个socketid 发送协议数据，如何socketid 不存在，会抛异常
        :param packet:
        :param sockid:
        :return:
        """
        if sockid not in self.__socks:
            VLog.Error("[PTC] uid:{0} sockid :{1} is not exist!", self.__uid, sockid)
            return
        # 发送数据
        self.__SendPacket(packet,sockid,self.MSG_PACKET)

    def CreatePacket(self,data=None):
        """
        创建协议包
        :return: 返回一个Packet对象
        """
        return Packet(data)

    def OnReceive(self, sockid, data):
        """
        收到数据
        :param sockid:
        :param data:
        :return:
        """
        begin_time = time.time() * 1000
        # 这里为什么会走VSocketMgr 主要是希望可以明确 这个返回是来自网络线程
        self.__cachePacketData.position = self.__cachePacketData.length()
        self.__cachePacketData.writeMulitBytes(data)
        self.__cachePacketData.position = 0
        length = self.__cachePacketData.length()
        # 这里的分包只是分底层组装的包，具体服务器返回的协议内容有没有完整，需要OnMessage中自己判断
        while length - self.__cachePacketData.position > 0:
            # 长度不足
            if length - self.__cachePacketData.position < 19:
                break
            # 开始标记不对
            head_flag = self.__cachePacketData.readUnsignedByte() & 0xFF
            if head_flag != 0xEF:
                self.__cachePacketData.clear()
                VLog.Error("[PTC] Recv Packet Head ERROR! uid:{0} sockid:{1} flag:{2}", self.__uid, sockid, head_flag)
                break
            pack_len = self.__cachePacketData.readUnsignedInt()
            # 协议长度不足
            if length - self.__cachePacketData.position < pack_len:
                self.__cachePacketData.position = length
                break
            uid = self.__cachePacketData.readUnsignedInt()
            idx = self.__cachePacketData.readUnsignedInt()
            rindex = self.__cachePacketIndex[sockid]["ReceiveIdx"]
            # 协议序号错了
            if rindex + 1 != idx:
                self.__cachePacketData.clear()
                VLog.Error("[PTC] Recv Packet Index ERROR!!!!! uid:{0} local:{1},server:{2}", self.__uid, rindex+1, idx)
                break
            self.__cachePacketIndex[sockid]["ReceiveIdx"] += 1

            msgID = self.__cachePacketData.readUnsignedShort()
            sockid = self.__cachePacketData.readUnsignedInt()

            if msgID == self.MSG_DISCONNECT:
                self.OnClose(sockid)
            elif msgID == self.MSG_PACKET:
                rdata = self.__cachePacketData.readMulitBytes(pack_len - (4 + 4 + 2 + 4))
                try:
                    VSocketMgr.GetInstance().OnMessage(self, sockid, Packet(rdata))
                except Exception as e:
                    VLog.Trace(e)
                remaining = length - self.__cachePacketData.position
                if remaining <= 0:
                    self.__cachePacketData.clear()
                else:
                    cdata = self.__cachePacketData.readMulitBytes(remaining)
                    self.__cachePacketData.reset(data)
                length = self.__cachePacketData.length()
            else:
                self.__cachePacketData.clear()
                VLog.Error("[PTC] Recv Pack MsgID: {0} error!!!!! uid:{1}", msgID, self.__uid)
                break
        cost_time = time.time() * 1000 - begin_time
        if cost_time > 20:
            VLog.Info("[PTC] OnReceice Cost Time:{0}ms UID:{1} sockID:{2}", cost_time, self.__uid, sockid)

    def OnClose(self, sockid):
        """
        服务器关闭
        :param sockid:
        :return:
        """
        VLog.Info("[PTC] Server Closed the socket uid:{0} , sockID:{1}", self.__uid, sockid)
        VSocketMgr.GetInstance().OnDisconnect(self, sockid)
        self.Disconnect(sockid, False)
