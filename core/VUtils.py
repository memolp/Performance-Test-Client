# -*- coding:utf-8 -*-

"""
  工具箱
"""

import random


def avg(iter, key=None):
    """
    自定义求平均值
    :param iter:
    :param key:
    :return:
    """
    nlen = len(iter)
    if nlen == 0:
        return 0
    total_v = 0
    for i in iter:
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



if __name__ == "__main__":
    a = [1,2,3,4,5,6,7,8]
    r = Random()
    for x in r.taker(a,3):
        print(x)
        if not x:
            break

