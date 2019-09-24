# -*- coding:utf-8 -*-

# 用户创建完成后调用
def OnInit(vuser):
    #print("OnInit")
    vuser.Connect("127.0.0.1", 4567, 0, 0)


# 收到协议调用 (packet需要手动分包)
def OnMessage(vuser, sockid, packet):
    #print("OnMessage",packet)
    vuser.SetBusy(False)
    vuser.EndTranslation("A")

# 并发执行调用(count未执行的次数)
def OnConcurrence(vuser, count):
    #print("OnConcurrence")
    vuser.SetBusy(True)
    packet = vuser.CreatePacket()
    packet.writeUTFBytes("2"*100)
    vuser.StartTranslation("A")
    vuser.Send(packet,0)

# 网络链接断开
def OnDisconnect(vuser, sockid):
    print("OnDisconnect",sockid,vuser.GetUID())
    #vuser.Disconnect(sockid)
    vuser.SetData("init", None)

def OnConnected(vuser,sockid):
    """"""
    #print("Connected: ",sockid,vuser.GetUID())
    vuser.SetInitCompleted(True)
    vuser.SetBusy(False)