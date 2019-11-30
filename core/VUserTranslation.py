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
    VUser 事务统计
    TPS = 并发用户数 / 平均响应时间(秒)
    并发数 = TPS * 平均响应时间（秒）
author:
    JeffXun
"""


import time

from core.utils.VLog import VLog
from core.utils.VUtils import *


class VTranslation:
    """
    每轮的事务统计
    """
    FORMAT_STR = "[{0}] Round {1}, Total {2}, Finish {3}, Response {4} ms, Rate {5}%, TPS {6}"
    FORMAT_STR2= "[{0}] Total {1}, Finish {2}, Response {3} ms, Rate {4} %, TPS {5}"

    def __init__(self, round):
        """
        轮次
        :param round:
        """
        self.round = round
        # 完成事务的记录 - 已完成的事务，不需要区分用户
        self.translation_end = {}
        # 用户执行中的事务记录 - 执行中的需要区分用户
        self.user_trans_run = {}
        #  总事务数 和 已完成事务数
        self.total_trans = 0
        self.finish_trans = 0

    def Append(self, uid, mname):
        """
        增加事务记录
        :param uid:
        :param mname:
        :return:
        """
        # 第一层 事务名称
        if mname not in self.user_trans_run:
            self.user_trans_run[mname] = {}
        # 第二层 用户id
        if uid not in self.user_trans_run[mname]:
            self.user_trans_run[mname][uid] = []

        # 记录一个开始时间
        self.user_trans_run[mname][uid].append(time.time() * 1000)

        self.total_trans += 1

    def Finish(self, uid, mname, timestamp=0):
        """
        事务完成
        :param uid:
        :param mname:
        :param timestamp: 指定完成时间， 0表示当前时间
        :return:
        """
        # 记录结束时间
        e_time = time.time() * 1000 if timestamp == 0 else timestamp
        if mname not in self.user_trans_run:
            VLog.Error("translation {0} is not exist", mname)
            return

        if uid not in self.user_trans_run[mname]:
            VLog.Error("translation {0} and uid {1} is not exist", mname, uid)
            return

        # 拿到事务开始时间
        s_time = self.user_trans_run[mname][uid].pop(0)
        # 响应时间
        s_response_time = e_time - s_time

        if mname not in self.translation_end:
            self.translation_end[mname] = [s_response_time]
        else:
            self.translation_end[mname].append(s_response_time)

        self.finish_trans += 1

    def get_trans_n_count(self, mname):
        """
        获取未完成的事务数量
        :param mname:
        :return:
        """
        total = 0
        for uid in self.user_trans_run[mname]:
            total += len(self.user_trans_run[mname][uid])
        return total

    def has_trans(self):
        """
        返回是否有数据
        :return:
        """
        return self.total_trans > 0

    def isEmpty(self):
        """
        判断是否没有添加事务
        :return:
        """
        return self.total_trans == 0 and self.finish_trans == 0

    def isAllDone(self):
        """
        判断事务全部执行完成
        :return:
        """
        return self.total_trans == self.finish_trans

    def trans_finish_statics(self, strans_info=None, avg_percent=0.2):
        """
        事务完成统计
        :param strans_info:
        :param avg_percent:
        :return:
        """
        strans_info = strans_info if strans_info else {}
        for mname in self.translation_end.keys():
            u_finish = self.get_trans_n_count(mname)
            f_finish = len(self.translation_end[mname])
            t_trans = u_finish + f_finish
            avg_response = round(avg(self.translation_end[mname], percent=avg_percent), 2)
            if mname not in strans_info:
                strans_info[mname] = {"total": t_trans, "finish": f_finish, "response": avg_response, "record": 1}
            else:
                strans_info[mname]["total"] += t_trans
                strans_info[mname]['finish'] += f_finish
                strans_info[mname]["response"] += avg_response
                strans_info[mname]["record"] += 1
        return strans_info

    def display_translation(self):
        """
        显示事务
        :return:
        """
        trans_info = self.trans_finish_statics()
        for mname in trans_info.keys():
            trans = trans_info[mname]
            trans_rate = round(trans['finish'] / trans['total'], 4) * 100
            result = self.FORMAT_STR.format(mname, self.round, trans['total'], trans['finish'], trans['response'],
                                             trans_rate, int(trans['finish'] / trans['response'] * 1000))
            VLog.Info(result)


class VUserTranslation(object):
    """
    用户事务统计
    """
    def __init__(self):
        """"""
        self.round_trans = []
        self.round_trans_count = 0
        self.timer_thread = None
        self.trans_record = {}

    def create_round_translation(self, r_round):
        """
        创建一个事务
        :param r_round: 测试轮数
        :return:
        """
        trans = VTranslation(r_round)
        self.round_trans.append(trans)
        self.round_trans_count += 1
        return trans

    def _all_translation_display(self):
        """
        打印全部事务
        :return:
        """
        for mname in self.trans_record.keys():
            trans = self.trans_record[mname]
            trans_rate = round(trans['finish'] / trans['total'], 4) * 100
            avg_response = round(trans['response'] / trans['record'], 2)
            msg = VTranslation.FORMAT_STR2.format(mname, trans['total'], trans['finish'], avg_response,
                                                  trans_rate, int(trans['finish'] / trans['response'] * 1000))
            VLog.Info(msg)

    def timer_of_translation_display(self, last_index=5):
        """
        打印事务完成情况
        :param last_index:
        :return:
        """
        index = 0
        size = len(self.round_trans)
        while index < size - last_index:
            trans = self.round_trans[index]
            if trans.isEmpty():
                self.round_trans.pop(index)
                break

            if trans.isAllDone():
                self.trans_record = trans.trans_finish_statics(self.trans_record)
                trans.display_translation()
                self.round_trans.pop(index)
                break
            index += 1

    def start_translation_display(self, delay_time=1.0):
        """
        开始打印事务
        :param delay_time:
        :return:
        """
        self.cancel_thread()
        # 定时器启动
        self.timer_thread = IntervalTimer(delay_time, self.timer_of_translation_display)
        self.timer_thread.start()

    def end_translation_display(self):
        """
        结束时打印全部的事务数据
        :return:
        """
        self.cancel_thread()
        VLog.Info("============================= Concurrence Translation =============================")
        self._all_translation_display()
        VLog.Info("============================= Concurrence Translation =============================")

    def cancel_thread(self):
        """
        取消线程调用
        :return:
        """
        if self.timer_thread is not None and self.timer_thread.isAlive():
            self.timer_thread.cancel()

    def is_all_translation_end(self):
        """
        返回是否所有事物都完成了
        :return:
        """
        return len(self.round_trans) == 0
