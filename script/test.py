# -*- coding:utf-8 -*-

# 用户创建完成后调用
def OnInit(vuser):
    #print("OnInit")
    pass


# 收到协议调用 (packet需要手动分包)
def OnMessage(vuser, sockid, packet):
    #print("OnMessage",packet)
    vuser.EndTranslation("A")


# 并发执行调用(count未执行的次数)
def OnConcurrence(vuser, count):
    #print("OnConcurrence")
    if vuser.GetData("init") is None:
        vuser.Connect("127.0.0.1", 7091, 0, 1)
        #vuser.Connect("14.215.177.39",80,0)
        vuser.SetData("init",1)
    else:
        packet = vuser.CreatePacket()
        packet.writeUTFBytes("hello!!!")
        vuser.StartTranslation("A")
        vuser.Send(packet,0)

# 网络链接断开
def OnDisconnect(vuser, sockid):
    print("OnDisconnect",sockid,vuser.GetUID())
    #vuser.Disconnect(sockid)
    vuser.SetData("init", None)