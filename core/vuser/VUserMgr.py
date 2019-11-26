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
    VUser 管理器
author:
    JeffXun
"""

import time
import math
import threading


import concurrent.futures as concurrent
import core.utils.VUtils as VUtils

from core.vuser.VUser import VUser
from core.utils.VUtils import *
from core.utils.VLog import VLog




class VUserMgr:
    """
    VUser manager and concurrence
    """
    _instance = None
    # 默认一直运行
    RUN_TEST_TIMES = -1
    # 并发线程池
    TPS_THREAD_NUM = 2

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
        self.__vuserList = DictArray()
        self.__userCount = 0
        self.__tps = 0
        self.__index = 0
        self.__random = VUtils.Random()
        self.__testRunning = False
        self.__executor = concurrent.ThreadPoolExecutor(max_workers=self.TPS_THREAD_NUM)

    def GetAllUsers(self):
        """
        返回用户列表
        :return:
        """
        return self.__vuserList

    def GetUserByUID(self, uid):
        """
        获取user
        :param uid:
        :return:
        """
        return self.__vuserList.get(uid)

    def Stop(self):
        """
        停止测试
        :return:
        """
        self.__testRunning = False

    def CreateVUser(self, count, tps, index=0):
        """
        创建压测用户
        :param count: 用户数量
        :param tps: 并发数
        :param index: 起始标记
        :return:
        """
        self.__userCount = count
        self.__tps = tps
        # 清除旧数据
        self.__vuserList.clear()
        # 创建用户
        for i in range(count):
            user = VUser(i + index)
            self.__vuserList.append(user)

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
                transaltion_info[key]["avg"].append(avg(trans, key=lambda x: x.Cost(), percent=0.2))
        return transaltion_info

    # 事务统计打印的格式
    TRANSLATION_INFO = "[PTC] {0}|in:{1}|ed:{2}|max:{3} ms|avg:{4} ms|{5}%"

    def TickerThread(self):
        """
        定时线程
        :return:
        """
        while self.__testRunning:
            start_time = time.time()
            # 事务信息
            transaltion_info = {}
            # 用户列表
            for vuser in self.__vuserList:
                try:
                    # 状态回调方法执行
                    callback = vuser.GetStateCallback()
                    if callback is not None:
                        callback(*vuser.GetStateCallbackArgs())
                    # 间隔执行
                    callback = vuser.GetTickCallback()
                    if callback is not None:
                        callback(start_time)
                except Exception as e:
                    VLog.Trace(e)
                # 统计事务
                self.CulTranslation(vuser, transaltion_info)

            #针对统计的事务进行打印输出
            for key,transinfo in transaltion_info.items():
                doing = transinfo["doing"]
                done = transinfo["done"]
                rate = done / (done + doing) * 100
                max_v = max(transinfo["max"], key=lambda x:x.Cost()).Cost() if len(transinfo["max"]) >0 else -1
                avg_v = avg(transinfo["avg"], percent=0.1) if len(transinfo["avg"]) >0 else -1
                VLog.Info(self.TRANSLATION_INFO, key, doing, done, round(max_v, 2), round(avg_v, 2), round(rate, 2))

            # 花费时间正常不会超过1秒
            cost_time = time.time() - start_time
            if cost_time < 1.0:
                time.sleep(1.0 - cost_time)
            else:
                VLog.Fatal("[PERFORMANCE] TickerThread function cost_time :{0}!!!!!!!!", cost_time)

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
        while self.__testRunning:
            count = 0
            for vuser in self.__vuserList:
                if vuser.GetInitCompleted():
                    count += 1
            VLog.Info("[PTC] Init Completed Client Count:{0}", count)
            if count/size >= percent:
                break
            else:
                time.sleep(1.0)
        VLog.Info("[PTC] Wait Client Init Completed ......end")

    def Start(self, script, delay=0.0):
        """
        启动
        :param script:
        :param delay:
        :return:
        """
        self.__testRunning = True
        # 启动定时器线程
        self._start_tick_thread()
        self.OnSceneRunning(script, delay, self.RUN_TEST_TIMES)

    def MultiStart(self, delay, scenes):
        """
        多场景测试
        :param delay:
        :param scenes:
        :return:
        """
        self.__testRunning = True
        self._start_tick_thread()
        index = 0
        size = len(scenes)
        while self.__testRunning and size > 0:
            scene = scenes[index]
            if scene['times'] <= scene['max_times'] or scene['max_times'] == -1:
                self.OnSceneRunning(scene['script'], delay, scene['times'])
                scene['times'] *= 2
            index += 1
            if index >= size:
                index = 0

    def OnSceneRunning(self, script, delay, times):
        """
        并发
        :param script:
        :param userList:
        :param delay:
        :param times:
        :return:
        """
        VLog.Info("[PTC] Call VUser OnInit ............................")
        # 调用初始化
        for users in self.__random.taker(self.__vuserList, self.__tps):
            for user in users:
                user.SetScene(script.CreateScene(user))
                self.OnInit(user)
            if delay > 0:
                time.sleep(delay)
        VLog.Info("[PTC] Call VUser OnInit ............................end")
        # 等待客户端初始化完成
        self._wait_client_initCompleted(0.9)
        # 等待一分钟后开始压测
        for i in range(0, 0, -1):
            VLog.Info("[PTC] Wait for {0} seconds to Testing ...........", i - 1)
            time.sleep(1)
        VLog.Info("[PTC] Begin Concurrence ............................")
        # 主循环
        round_count = 0
        while self.__testRunning and (times == -1 or (round_count < times)):
            start_time = time.time()
            users = self.__random.poll(self.__vuserList, self.__tps, lambda x: x.IsFinished())
            if len(users) < self.__tps:
                VLog.Info("[PTC] Concurrence TPS :{0} ,expect:{1}", len(users), self.__tps)

            tasks = [self.__executor.submit(self._users_concurrent, users, i, round_count)
                     for i in range(self.TPS_THREAD_NUM)]
            concurrent.wait(tasks, return_when=concurrent.ALL_COMPLETED)
            # # 执行任务
            # for vuser in users:
            #     self.OnConcurrence(vuser, round_count)
            # 每执行一轮，+1
            round_count += 1
            # 花费时间正常不会超过1秒
            cost_time = time.time() - start_time
            # 超过0.6就打印出来，防止sleep的问题影响并发
            if cost_time > 0.6:
                VLog.Fatal("[PERFORMANCE] Start function cost_time :{0}!!!!!!!!", cost_time)
            if cost_time < 1.0:
                time.sleep(1.0 - cost_time)
        VLog.Info("[PTC] End Concurrence ............................")

    def _users_concurrent(self, users, i, round_count):
        """
        用户并发
        :param users:
        :param i:
        :param round_count:
        :return:
        """
        size = len(users)
        split_num = math.ceil(size / self.TPS_THREAD_NUM)
        index = i * split_num
        while index < size and index < (i+1)*split_num:
            user = users[index]
            index += 1
            self.OnConcurrence(user, round_count)

    def OnInit(self, vuser):
        """
        执行user初始化
        :param vuser:
        :return:
        """
        try:
            vuser.GetScene().OnInit()
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
            vuser.GetScene().OnConcurrence(count)
        except Exception as e:
            VLog.Trace(e)


