# -*- coding:utf-8 -*-

"""
 VUser 管理器
"""

import time
import threading
import traceback

from concurrent.futures import ThreadPoolExecutor
from core.VUser import VUser
from core.VUtils import *

class VUserMgr:
    """
    VUser manager and concurrence
    """
    _instance = None

    @staticmethod
    def GetInstance():
        """
        单例
        :return:
        """
        if VUserMgr._instance is None:
            VUserMgr._instance = VUserMgr()
        return VUserMgr._instance

    def __init__(self):
        """"""
        self.__vuserList = []
        self.__script = None
        self.__userCount = 0
        self.__tps = 0
        self.__threadExecutor = None
        self.__index = 0

    def CreateVUser(self, script, count, tps):
        """
        创建压测用户
        :param script: 压测脚本
        :param count: 用户数量
        :param tps: 并发数
        :return:
        """
        self.__script = script
        self.__userCount = count
        self.__tps = tps

        # 创建用户
        for i in range(count):
            user = VUser(i)
            self.__vuserList.append(user)

        # 根据并发创建对应数量的线程池
        self.__threadExecutor = ThreadPoolExecutor(self.__tps)

        # 调用初始化
        for user in self.__vuserList:
            self.OnInit(user)

    def StateThread(self):
        """
        vuser状态线程
        :return:
        """
        while True:
            start_time = time.time()
            transaltion_info = {}
            # 状态回调方法执行
            for vuser in self.__vuserList:
                try:
                    callback = vuser.GetStateCallback()
                    if callback is not None:
                        callback(vuser,*vuser.GetStateCallbackArgs())
                    callback = vuser.GetTickCallback()
                    if callback is not None:
                        callback(vuser)
                except Exception as e:
                    print(traceback.format_exc())

                transaltions, finishtrans = vuser.GetTranslationInfo()
                for key,trans in transaltions.items():
                    if key not in transaltion_info:
                        transaltion_info[key] = {"doing":0,"done":0,"max":[],"avg":[]}
                    transaltion_info[key]["doing"] += len(trans)
                for key,trans in finishtrans.items():
                    if key not in transaltion_info:
                        transaltion_info[key] = {"doing":0,"done":0,"max":[],"avg":[]}
                    transaltion_info[key]["done"] += len(trans)
                    if len(trans) > 0:
                        transaltion_info[key]["max"].append(max(trans, key=lambda x:x.Cost()))
                        transaltion_info[key]["avg"].append(avg(trans, key=lambda x:x.Cost()))

            fmt_label = "{0}|in:{1}|ed:{2}|max:{3} ms|avg:{4} ms|{5}%"
            for key,transinfo in transaltion_info.items():
                rate = transinfo["done"] / (transinfo["done"] + transinfo["doing"]) * 100
                max_v = max(transinfo["max"],key=lambda x:x.Cost()).Cost() if len(transinfo["max"]) >0 else -1
                avg_v = avg(transinfo["avg"]) if len(transinfo["avg"]) >0 else -1
                print(fmt_label.format(key,transinfo["doing"],transinfo["done"],round(max_v,2),round(avg_v,2),round(rate,2)))

            # 花费时间正常不会超过1秒
            cost_time = time.time() - start_time
            if cost_time < 1.0:
                time.sleep(1.0 - cost_time)
            else:
                print("cost_time :{0}!!!!!!!!".format(cost_time))

    def Start(self):
        """
        启动
        :return:
        """
        round_count = 0
        # 状态线程执行
        stateThread = threading.Thread(target=self.StateThread,args=())
        stateThread.start()
        # 主循环
        while True:
            start_time = time.time()
            users = self._GetVUser(self.__tps)
            # 执行任务
            for vuser in users:
                task = self.__threadExecutor.submit(self.OnConcurrence,vuser, round_count)
                vuser.SetTask(task)
            # 每执行一轮，+1
            round_count += 1

            # 花费时间正常不会超过1秒
            cost_time = time.time() - start_time
            if cost_time < 1.0:
                time.sleep(1.0 - cost_time)
            else:
                print("cost_time :{0}!!!!!!!!".format(cost_time))

    def _GetVUser(self, num):
        """
        获取user执行任务
        :param num:
        :return:
        """
        users = []
        # 从当前位置获取user，满足数量则返回
        for i in range(self.__index, len(self.__vuserList)):
            vuser = self.__vuserList[i]
            if vuser.TaskFinish():
                users.append(vuser)
            if len(users) >= num:
                self.__index += num
                return users
        # 从头开始获取，满足数量返回
        for i in range(0, self.__index):
            vuser = self.__vuserList[i]
            if vuser.TaskFinish():
                users.append(vuser)
            if len(users) >= num:
                self.__index = i
                return users
        # 不满足也返回
        return users



    def OnInit(self, vuser):
        """
        执行user初始化
        :param vuser:
        :return:
        """
        try:
            self.__script.OnInit(vuser)
        except Exception as e:
            print(traceback.format_exc())

    def OnConcurrence(self, vuser, count):
        """
        [thread]执行并发
        :param vuser:
        :param count:
        :return:
        """
        try:
            self.__script.OnConcurrence(vuser, count)
        except Exception as e:
            print(traceback.format_exc())