# -*- coding:utf-8 -*-

"""
 压测脚本模板
"""

str_template = """
# -*- coding:utf-8 -*-

# 用户创建完成后调用
def OnInit(vuser):
    pass
    
# 收到协议调用 (data需要手动分包)
def OnMessage(vuser, sockid, packet):
    pass

# 并发执行调用(count未执行的次数)
def OnConcurrence(vuser, count):
    pass

# 网络链接断开
def OnDisconnect(vuser, sockid):
    pass

"""