# -*- coding:utf-8 -*-

"""
 压测脚本模板
"""

str_template = """
# -*- coding:utf-8 -*-

def OnInit(vuser):
    # 用户创建完成后调用
    pass
    
def OnMessage(vuser, sockid, packet):
    # 收到协议调用 (packet需要手动分包)
    pass

def OnConcurrence(vuser, count):
    # 并发执行调用(count未执行的次数)
    pass

def OnDisconnect(vuser, sockid):
    # 网络链接断开
    pass

"""