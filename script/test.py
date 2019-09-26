# -*- coding:utf-8 -*-


from core.vuser.VUserScene import VUserScene


class NewScene(VUserScene):
    """

    """
    def __init__(self, vuser, name):
        """
        :param vuser: 用户
        :param name: 场景名
        """
        super(NewScene,self).__init__(vuser,name)

    def OnMessage(self, sock_id, packet):
        """
        网络收包返回
        :param sock_id:
        :param packet: 需处理粘包和不完整包
        :return:
        """
        self.vUser.SetBusy(False)
        self.vUser.EndTranslation("A")

    def OnConcurrence(self, count):
        """
        并发执行调用
        :param count:
        :return:
        """
        self.vUser.SetBusy(True)
        packet = self.vUser.CreatePacket()
        packet.writeUTFBytes("2" * 100)
        self.vUser.StartTranslation("A")
        self.vUser.Send(packet, 1)

    def OnInit(self):
        """
        vuser创建后调用
        :return:
        """
        #self.vUser.Connect("127.0.0.1", 4567, 0, 0)
        self.vUser.Connect("127.0.0.1", 4567, 1, 0)

    def OnDisconnect(self, sock_id):
        """
        网络链接断开调用
        :param sock_id: 调用vuser.connect时传入的sock_id
        :return:
        """
        pass

    def OnConnected(self, sock_id):
        """
        网络链接完成
        :param sock_id: 调用vuser.connect时传入的sock_id
        :return:
        """
        self.vUser.SetInitCompleted(True)
        self.vUser.SetBusy(False)




def CreateScene(vuser):
    """
    创建场景时会调用此方法
    """
    return NewScene(vuser,"新场景")