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
    线程池
author:
    JeffXun

"""

import os
import queue
import time
import threading

from core.utils.VLog import VLog


class VTask:
    INIT = 0
    RUNNING = 1
    END = 2
    def __init__(self, fn, *arg, **kwargs):
        """"""
        self.__state = VTask.INIT
        self.__fn = fn
        self.__arg = arg
        self.__kwargs = kwargs
        self.mRoll = False

    def run(self):
        """ """
        self.__state = VTask.RUNNING
        try:
            self.__fn(*self.__arg,**self.__kwargs)
        except Exception as e:
            print(e)
        self.__state = VTask.END

    def done(self):
        """ """
        return self.__state == VTask.END


class ThreadExecutor:
    """线程池"""
    def __init__(self, max_workers=None, threadname=''):
        """ """
        if max_workers is None:
            # 默认采用CPU数量的线程池
            max_workers = (os.cpu_count() or 1)
        if max_workers <= 0:
            raise ValueError("max_workers must be greater than 0")
        # 环任务
        self.__missions = queue.Queue()
        # 单任务
        self.__tasks = queue.SimpleQueue()
        # 线程集合
        self.__threads = set()
        # 线程数量
        self.__max_workers = max_workers
        # 线程名
        self.__thread_name = threadname or "ThreadExecutor"

    def submit(self, fn, *args, **kwargs):
        """
        提交单任务，执行完就结束
        :param fn:
        :param args:
        :param kwargs:
        :return:
        """
        task = VTask(fn, *args, **kwargs)
        self.__tasks.put(task, False)
        self._adjust_thread_count()
        return task

    def create(self, fn, *args, **kwargs):
        """
        创建环任务，执行完后继续放入队列执行
        :param fn:
        :param args:
        :param kwargs:
        :return:
        """
        task = VTask(fn,*args, **kwargs)
        task.mRoll = True
        self.__tasks.put(task, False)
        self._adjust_thread_count()
        return task

    def stop(self):
        """
        停止
        :return:
        """
        self.__tasks.put(None)

    def _adjust_thread_count(self):
        """ """
        num_threads = len(self.__threads)
        if num_threads < self.__max_workers:
            thread_name = '%s_%d' % (self.__thread_name or self, num_threads)
            t = threading.Thread(name=thread_name, target=self._worker, args=())
            t.daemon = True
            t.start()
            self.__threads.add(t)


    def _worker(self):
        """ """
        begin_time = time.time() * 1000
        while True:
            try:
                task = self.__tasks.get(block=True)
                if VLog.Performance_Log:
                    begin_time = time.time() * 1000
                if task is None:
                    self.__tasks.put(None)
                    break
                task.run()
                if task.mRoll:
                    self.__tasks.put(task)
                if VLog.Performance_Log:
                    cost = time.time() * 1000 - begin_time
                    if cost > 900:
                        VLog.Fatal("[PERFORMANCE] {0} work execute with {1} ms", self.__thread_name, cost)
            except queue.Empty:
                pass