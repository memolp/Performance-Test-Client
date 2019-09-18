# -*- coding:utf-8 -*-

"""
  工具箱
"""

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