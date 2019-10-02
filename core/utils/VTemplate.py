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
    压测脚本模板
author:
    JeffXun
"""

str_template = """# -*- coding:utf-8 -*-

\"\"\"
压测场景，继承自VUserScene类，或者继承自VUserScene的子类
\"\"\"

from core.vuser.VUserScene import VUserScene

class NewScene(VUserScene):
    def __init__(self, vuser, name):
        \"\"\" 
        :param vuser: 用户
        :param name: 场景名
        \"\"\"
        super(NewScene,self).__init__(vuser,name)

    def OnMessage(self, sock_id, packet):
        \"\"\"
        网络收包返回
        :param sock_id:
        :param packet: 需处理粘包和不完整包
        :return:
        \"\"\"
        pass

    def OnConcurrence(self, count):
        \"\"\"
        并发执行调用
        :param count:
        :return:
        \"\"\"
        pass

    def OnInit(self):
        \"\"\"
        vuser创建后调用
        :return:
        \"\"\"
        pass

    def OnDisconnect(self, sock_id):
        \"\"\"
        网络链接断开调用
        :param sock_id: 调用vuser.connect时传入的sock_id
        :return:
        \"\"\"
        pass

    def OnConnected(self, sock_id):
        \"\"\"
        网络链接完成
        :param sock_id: 调用vuser.connect时传入的sock_id
        :return:
        \"\"\"
        pass


def CreateScene(vuser):
    \"\"\"
    创建场景时会调用此方法
    \"\"\"
    return NewScene(vuser,"新场景")
"""
