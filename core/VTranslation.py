# -*- coding:utf-8 -*-

"""
 VUser 事务统计
"""

import time

class VTranslation:
    """
    事务统计
    """
    def __init__(self,vuser, mname):
        """"""
        self.__vuser = vuser
        self.__mname = mname
        # 毫秒
        self.__start = time.time() * 1000
        self.__end   = self.__start
        self.__cast  = -1

    def Finish(self):
        """"""
        self.__end = time.time() * 1000
        self.__cast = self.__end - self.__start

    def Cost(self):
        """"""
        return self.__cast