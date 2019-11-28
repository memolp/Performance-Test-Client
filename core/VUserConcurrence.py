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
    压测用户管理
author:
    JeffXun
"""

import time
import math
import threading

import concurrent.futures as concurrent
import core.utils.VUtils as VUtils

from core.vuser.VUser import VUser
from core.utils.VLog import VLog
from core.VUserTranslation import VUserTranslation


class VUserConcurrence:
    """
    Vuser manager and concurrence
    """
    def __init__(self):
        """"""
        self.rpc_client = None
        self.user_num = -1
        self.tps = -1
        self.tps_thread = -1
        # 方便用户并发获取
        self.user_peak = VUtils.Random()
        # 用户列表
        self.users_list = []
        # 并发线程池对象
        self.executor = None
        # 定时器线程
        self.timer_thread = None
        # 用户事务统计
        self.user_trans = VUserTranslation()

    def set_rpc_obj(self, rpc_client):
        """
        设置rpc_client
        :param rpc_client:
        :return:
        """
        self.rpc_client = rpc_client

    def set_concurrence(self, tps, tps_thread=2):
        """
        设置并发用户数量和并发数
        :param tps:
        :param tps_thread: 并发线程池数量
        :return:
        """
        self.tps = tps
        self.tps_thread = tps_thread
        self.executor = concurrent.ThreadPoolExecutor(max_workers=self.tps_thread)

    def set_users(self, user_num, index=0):
        """
        设置并发用户
        :param user_num:
        :param index:
        :return:
        """
        self.user_num = user_num
        i = 0
        while i < user_num:
            uid = i + index
            user = VUser(uid, self.rpc_client)
            self.users_list.append(user)
            i += 1

    def get_users(self):
        """
        获取用户列表
        :return:
        """
        return self.users_list

    def run_concurrence(self, script_module, run_times=-1, init_delay=0):
        """
        执行并发
        :param script_module: 脚本模块
        :param run_times: 压测轮数（秒数） 压测每秒执行一次并发，因此轮数和秒数相等
        :param init_delay: 初始化延迟
        :return:
        """
        return self._on_scene_concurrence(script_module, init_delay, run_times)

    def run_multi_concurrence(self, init_delay, scenes):
        """
        多场景测试
        :param init_delay:
        :param scenes:
        :return:
        """
        index = 0
        size = len(scenes)
        while size > 0:
            scene = scenes[index]
            if scene['times'] <= scene['max_times'] or scene['max_times'] == -1:
                self._on_scene_concurrence(scene['script'], init_delay, scene['times'])
                scene['times'] *= 2
            index += 1
            if index >= size:
                index = 0

    def _begin_init(self, script_module, init_delay):
        """
        开始初始化
        :param script_module:
        :param init_delay:
        :return:
        """
        VLog.Info("[PTC] Call VUser OnInit ............................")
        # 调用初始化 -每次从列表中取出指定数量的vuser
        for users in self.user_peak.taker(self.users_list, self.tps):
            for user in users:
                user.SetScene(script_module.CreateScene(user))
                self._on_user_init(user)
            VLog.Info("[PTC] VUser {0} was Called OnInit ..............end", len(users))
            if init_delay > 0:
                time.sleep(init_delay)
        VLog.Info("[PTC] Call VUser OnInit ............................end")

    def _wait_init_completed(self, percent=1.0):
        """
        等待客户端初始化完成
        :param percent: 初始化完成的客户端占比
        :return:
        """
        VLog.Info("[PTC] Wait Client Init Completed ......")
        size = len(self.users_list)
        while self.users_list:
            count = 0
            for vuser in self.users_list:
                if vuser.GetInitCompleted():
                    count += 1
            VLog.Info("[PTC] Init Completed Client Count:{0}", count)
            if count/size >= percent:
                break
            else:
                time.sleep(1.0)
        VLog.Info("[PTC] Wait Client Init Completed ......end")

    def _end_init(self, wait_time=60):
        """
        结束初始化
        :param wait_time:
        :return:
        """
        for i in range(wait_time, 0, -1):
            VLog.Info("[PTC] Wait for {0} seconds to Testing ...........", i - 1)
            time.sleep(1)

    def _on_scene_concurrence(self, script, init_delay, run_times):
        """
        并发
        :param script:
        :param init_delay:
        :param run_times:
        :return:
        """
        self._start_tick_thread()
        # 对用户执行初始化
        self._begin_init(script, init_delay)
        # 等待客户端初始化完成
        self._wait_init_completed(1.0)
        # 等待一分钟后开始压测
        self._end_init(5)
        # 启动事务打印
        self.user_trans.start_translation_display()

        VLog.Info("[PTC] Begin Concurrence ............................")
        # 主循环
        round_ = 0
        while run_times == -1 or (round_ < run_times):
            start_time = time.time()
            # 获取并发用户列表
            users = self.user_peak.poll(self.users_list, self.tps, lambda x: x.IsFinished())
            if len(users) < self.tps:
                VLog.Info("[PTC] Concurrence TPS :{0} ,expect:{1}", len(users), self.tps)

            translation = self.user_trans.create_round_translation(round_)

            # 执行并发
            tasks = [self.executor.submit(self._users_concurrent, users, i, round_, translation)
                     for i in range(self.tps_thread)]
            concurrent.wait(tasks, return_when=concurrent.ALL_COMPLETED)

            # 每执行一轮，+1
            round_ += 1

            # 花费时间正常不会超过1秒
            cost_time = time.time() - start_time
            # 超过0.6就打印出来，防止sleep的问题影响并发
            if cost_time > 0.6:
                VLog.Fatal("[PERFORMANCE] _on_scene_concurrence cost_time :{0}!!!!!!!!", cost_time)
            if cost_time < 1.0:
                time.sleep(1.0 - cost_time)
        VLog.Info("[PTC] End Concurrence ............................")
        # 结束时打印事务完成信息
        self.user_trans.end_translation_display()

    def _users_concurrent(self, users, i, round_count, translation):
        """
        用户并发
        :param users:
        :param i:
        :param round_count:
        :return:
        """
        size = len(users)
        split_num = math.ceil(size / self.tps_thread)
        index = i * split_num
        while index < size and index < (i+1)*split_num:
            user = users[index]
            user.SetTranslation(translation)
            index += 1
            self._on_user_concurrence(user, round_count)

    def _on_user_init(self, vuser):
        """
        执行user初始化
        :param vuser:
        :return:
        """
        try:
            vuser.GetScene().OnInit()
        except Exception as e:
            VLog.Trace(e)

    def _on_user_concurrence(self, vuser, count):
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

    def _timer_tick_thread(self, delay):
        """
        定时器线程
        :return:
        """
        start_time = time.time()
        # 用户列表
        for vuser in self.users_list:
            try:
                # 间隔执行
                callback = vuser.GetTickCallback()
                if callback is not None:
                    callback(start_time)
            except Exception as e:
                VLog.Trace(e)

    def _start_tick_thread(self, delay=1.0):
        """
        启动定时器线程
        :param delay:
        :return:
        """
        if self.timer_thread is not None and self.timer_thread.isAlive():
            self.timer_thread.cancel()
        self.timer_thread = VUtils.IntervalTimer(delay, self._timer_tick_thread, args=[delay])
        self.timer_thread.start()
