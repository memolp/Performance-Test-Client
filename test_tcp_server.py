# -*- coding:utf-8 -*-

import socket

s = socket.socket()
s.bind(("10.6.7.69",7091))
s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 ) #端口复用的关键点
s.listen(5)
while True:
    c, a = s.accept()
    while True:
        buff = c.recv(25)
        print(c,a,buff)
        c.send(buff)
        
