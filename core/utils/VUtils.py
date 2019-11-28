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
    工具箱
author:
    JeffXun
"""

import random
import threading


def avg(iter, key=None, percent=0.0):
    """
    自定义求平均值
    :param iter:
    :param key:
    :param percent: 去除百分比（将列表中的最大最小值去掉一定后再计算平均值）
    :return:
    """
    nlen = len(iter)
    if nlen == 0:
        return 0
    # 要去除的数据
    del_num = int(nlen * percent / 2)
    if del_num >= nlen:
        return 0

    new_iter = iter
    if percent > 0:
        # 先转换成有序
        new_iter = sorted(iter, key=key)

    if del_num > 0:
        new_iter = new_iter[del_num:-del_num]
        
    # 计算新的平均数
    nlen = len(new_iter)
    total_v = 0
    for i in new_iter:
        if key is None:
            total_v += i
        else:
            total_v += key(i)
    return total_v / nlen

def __convert_n_bytes(n, b):
    """"""
    bits = b*8
    return (n + 2**(bits-1)) % 2**bits - 2**(bits-1)

def __convert_4_bytes(n):
    """"""
    return __convert_n_bytes(n, 4)

def GetHashCode(s):
    """
    获取字符串的hash值(类java)
    :param s:
    :return:
    """
    h = 0
    n = len(s)

    if isinstance(s,bytes):
        s = s.decode()

    for i, c in enumerate(s):
        h = h + ord(c)*31**(n-1-i)
    return __convert_4_bytes(h)


class Random:
    """
    随机操作类
    """
    def __init__(self):
        """"""
        self._poll_index = 0

    def sample(self, iterable, num):
        """
        随机采样
        :param iterable: 列表
        :param num: 每次采样的数量
        :return: [s1,...] 采集的结果
        """
        return random.sample(iterable, num)

    def poll(self, iterable, num, key=None):
        """
        轮询采样
        :param iterable: 列表
        :param num: 每次需要的数量
        :param key: 列表元素判断可用方法
        :return: [s1,....] 采样的结果
        """
        size = len(iterable)
        if size <= 0:
            return []

        result = []
        count  = 0
        for i in range(self._poll_index, size):
            obj = iterable[i]
            if key is None or key(obj):
                result.append(obj)
                count += 1
            if count >= num:
                self._poll_index = i + 1
                return result
        for i in range(0, self._poll_index):
            obj = iterable[i]
            if key is None or key(obj):
                result.append(obj)
                count += 1
            if count >= num:
                self._poll_index = i + 1
                return result
        return result

    def generator(self, iterable):
        """
        for in
        :param iterable:
        :return:
        """
        index = 0
        size = len(iterable)
        while index < size:
            yield iterable[index]
            index += 1

    def taker(self, iterable, num):
        """
        for task
        :param iterable:
        :param num:
        :return:
        """
        index = 0
        size = len(iterable)
        while index < size:
            yield iterable[index:index+num]
            index += num


class DictArray(object):
    """ """
    def __init__(self):
        """ """
        self.__Users = {}
        self.__size = 0

    def __iter__(self):
        index = 0
        while index < self.__size:
            yield self.__Users[index]
            index += 1

    def append(self, user):
        """"""
        self.__Users[self.__size] = user
        self.__size += 1

    def clear(self):
        """"""
        self.__Users.clear()
        self.__Users = {}
        self.__size = 0

    def __len__(self):
        """"""
        return self.__size

    def size(self):
        """"""
        return self.__size

    def get(self, key):
        """"""
        return self.__Users.get(key)

    def __getitem__(self, index):
        """"""
        if isinstance(index, slice):
            return list(self.__Users.values())[index]
        return self.__Users.get(index)


class IntervalTimer(threading.Thread):
    """Call a function after a specified number of seconds and reply run:

            t = IntervalTimer(30.0, f, args=None, kwargs=None)
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting
        间隔执行不要用thread.Timer 循环调用，这样开辟线程和销毁都是有消耗的
    """

    def __init__(self, interval, function, args=None, kwargs=None):
        threading.Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = threading.Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                self.function(*self.args, **self.kwargs)


if __name__ == "__main__":
    a = [1,2,3,4,5,6,7,8]
    b = DictArray()
    b.append(1)
    b.append(2)
    b.append(3)
    print(b[:2])
