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

def __convert_n_bytes(n, b):
    bits = b*8
    return (n + 2**(bits-1)) % 2**bits - 2**(bits-1)

def __convert_4_bytes(n):
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
