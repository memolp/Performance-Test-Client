# -*- coding:utf-8 -*-

"""
 VUser 管理器
"""

import time
import threading
import core.VLog as VLog
import core.VUtils as VUtils

from concurrent.futures import ThreadPoolExecutor
from core.VUser import VUser
from core.VUtils import *


class VUserMgr:
    """
    VUser manager and concurrence
    """
    _instance = None
    # 默认一直运行
    RUN_TEST_TIMES = -1

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
        self.__random = VUtils.Random()

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
        self.__threadExecutor = ThreadPoolExecutor(self.__tps*2)

    def CulTranslation(self,vuser, transaltion_info):
        """
        计算事务数据
        :param vuser:
        :param transaltion_info:
        :return:
        """
        # 获取并计算进行中和已完成的事务列表
        transaltions, finishtrans = vuser.GetTranslationInfo()
        # 统计进行中的事务数量
        for key, trans in transaltions.items():
            if key not in transaltion_info:
                transaltion_info[key] = {"doing": 0, "done": 0, "max": [], "avg": []}
            transaltion_info[key]["doing"] += len(trans)
        # 统计已完成的事务数量
        for key, trans in finishtrans.items():
            if key not in transaltion_info:
                transaltion_info[key] = {"doing": 0, "done": 0, "max": [], "avg": []}
            transaltion_info[key]["done"] += len(trans)
            # 已完成的事务 需要计算最大耗时和平均耗时
            if len(trans) > 0:
                transaltion_info[key]["max"].append(max(trans, key=lambda x: x.Cost()))
                transaltion_info[key]["avg"].append(avg(trans, key=lambda x: x.Cost()))
        return transaltion_info

    # 事务统计打印的格式
    TRANSLATION_INFO = "[PTC] {0}|in:{1}|ed:{2}|max:{3} ms|avg:{4} ms|{5}%"

    def TickerThread(self):
        """
        定时线程
        :return:
        """
        while True:
            start_time = time.time()
            # 事务信息
            transaltion_info = {}
            # 用户列表
            for vuser in self.__vuserList:
                try:
                    # 状态回调方法执行
                    callback = vuser.GetStateCallback()
                    if callback is not None:
                        callback(vuser,*vuser.GetStateCallbackArgs())
                    # 间隔执行
                    callback = vuser.GetTickCallback()
                    if callback is not None:
                        callback(vuser, start_time)
                except Exception as e:
                    VLog.Trace(e)

                # 统计事务
                self.CulTranslation(vuser, transaltion_info)

            #针对统计的事务进行打印输出
            for key,transinfo in transaltion_info.items():
                doing = transinfo["doing"]
                done = transinfo["done"]
                rate = done / (done + doing) * 100
                max_v = max(transinfo["max"],key=lambda x:x.Cost()).Cost() if len(transinfo["max"]) >0 else -1
                avg_v = avg(transinfo["avg"]) if len(transinfo["avg"]) >0 else -1
                VLog.Info(self.TRANSLATION_INFO, key, doing, done, round(max_v, 2), round(avg_v, 2), round(rate, 2))

            # 花费时间正常不会超过1秒
            cost_time = time.time() - start_time
            if cost_time < 1.0:
                time.sleep(1.0 - cost_time)
            else:
                VLog.Error("[PTC] TickerThread function cost_time :{0}!!!!!!!!",cost_time)

    def _start_tick_thread(self):
        """
        启动定时器线程
        :return:
        """
        # 定时线程启动
        p_thread = threading.Thread(target=self.TickerThread, args=())
        p_thread.start()

    def _wait_client_initCompleted(self, percent=1.0):
        """
        等待客户端初始化完成
        :param percent: 初始化完成的客户端占比
        :return:
        """
        VLog.Info("[PTC] Wait Client Init Completed ......")
        size = len(self.__vuserList)
        while True:
            count = 0
            for vuser in self.__vuserList:
                if vuser.GetInitCompleted():
                    count += 1
            VLog.Info("[PTC] Init Completed Client Count:{0}",count)
            if count/size >= percent:
                break
            else:
                time.sleep(1.0)
        VLog.Info("[PTC] Wait Client Init Completed ......end")

    def Start(self, delay=0.0):
        """
        启动
        :param delay:
        :return:
        """
        # 启动定时器线程
        self._start_tick_thread()
        # 调用初始化
        for users in self.__random.taker(self.__vuserList, self.__tps):
            for user in users:
                self.OnInit(user)
            if delay > 0:
                time.sleep(delay)
        # 等待客户端初始化完成
        self._wait_client_initCompleted(0.9)
        # 主循环
        round_count = 0
        while self.RUN_TEST_TIMES == -1 or (round_count < self.RUN_TEST_TIMES):
            start_time = time.time()
            users = self.__random.poll(self.__vuserList, self.__tps, lambda x:x.TaskFinish())
            if len(users) < self.__tps:
                VLog.Info("[PTC] Concurrence TPS :{0} ,expect:{1}", len(users), self.__tps)
            # 执行任务
            for vuser in users:
                task = self.__threadExecutor.submit(self.OnConcurrence, vuser, round_count)
                vuser.SetTask(task)

            # 每执行一轮，+1
            round_count += 1

            # 花费时间正常不会超过1秒
            cost_time = time.time() - start_time
            if cost_time < 1.0:
                time.sleep(1.0 - cost_time)
            else:
                VLog.Error("[PTC] Start function cost_time :{0}!!!!!!!!",cost_time)


    def OnInit(self, vuser):
        """
        执行user初始化
        :param vuser:
        :return:
        """
        try:
            self.__script.OnInit(vuser)
        except Exception as e:
            VLog.Trace(e)

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
            VLog.Trace(e)