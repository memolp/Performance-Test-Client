#压测脚本目录
#编写各个压测场景的脚本，执行时由压测底层调用



#伪代码

def OnInit(vuser):
    # 创建VUser完成后调用

    #状态机制，可以向vuser添加状态标记和执行函数，在事务操作中通过改变状态来调用不同的函数
    vuser.addState(1,function)
    vuser.addState(2,function)
    vuser.switchState(2) #执行切换状态后，会在OnConcurrence调用前先调用状态回调函数

def Disconnect(vuser, sockid):
    # 服务器主动断开链接

def OnMessage(vuser, sockid ,data):
    # 收到服务器协议--这个协议需要自己完成分包

def OnConcurrence(vuser,count):
    # 并发调用 concurrence;
    vuser.StartTranslation(name) # 如果多次调用StartTranslation添加事务统计，会同等匹配EndTranslation数量
    <do something.....>
    def OnMessage(vUser):   #在收到协议的函数里面判断事务是否完成 或者其他地方调用EndTranslation以结束对应的事务
        if is my translation :
        vuser.EndTranslation(name)

