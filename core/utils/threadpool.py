# -*- coding:utf-8 -*-

"""
 线程池
 线程池的任务执行说明：
    1、执行的任务分为两类：单任务（执行这个任务后就结束了），环任务（执行这个任务后，这个任务还有继续放入执行）
    2、线程池中存在两个队列，分别装载上面的两种任务
    2、执行的优先级：
        1) 单任务-优先被执行，直到队列为空结束
        2) 环任务-每次循环只执行一个环任务
"""

import os
import queue
import time
import threading


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
        t = time.time() * 1000
        task = VTask(fn, *args, **kwargs)
        self.__tasks.put(task, False)
        self._adjust_thread_count()
        cast = time.time() * 1000 - t
        if cast > 20:
            print("submit cast time > 20ms >>>>:::::{0}ms".format(cast))
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
        while True:
            try:
                task = self.__tasks.get(block=True)
                t = time.time() * 1000
                if task is None:
                    break
                task.run()
                if task.mRoll:
                    self.__tasks.put(task)
            except queue.Empty:
                pass
            cast = time.time() * 1000 - t
            if cast > 900:
                print("{0}_worker  cast time > 100ms >>>>:::::{1}ms".format(self.__thread_name,cast))