# -*- coding:utf-8 -*-

"""
  支持key-value或者.attr访问的类
"""


class VAttrObject(dict):
    """"""
    def __setattr__(self, key, value):
        self[key] = value
    def __getattr__(self, item):
        return self[item]



if __name__ == "__main__":
    o = VAttrObject()
    o['aa'] = 1
    o.tt = 2
    print(o.aa,o['tt'])