# -*- coding:utf-8 -*-

# 用户创建完成后调用
def OnInit(vuser):
    print("OnInit")
    vuser.Connect("127.0.0.1",7091)


# 收到协议调用 (data需要手动分包)
def OnMessage(vuser, sockid, packet):
    print("OnMessage",packet)


# 并发执行调用(count未执行的次数)
def OnConcurrence(vuser, count):
    print("OnConcurrence")
    packet = vuser.CreatePacket()
    packet.writeUTFBytes("sdasdasdsd")
    vuser.Send(packet)

# 网络链接断开
def OnDisconnect(vuser, sockid):
    print("OnDisconnect")