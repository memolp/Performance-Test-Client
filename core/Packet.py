# -*- coding:utf-8 -*-

"""
 协议包
"""

import struct
import binascii
from io import BytesIO


class Endian:
    """
    网络数据对齐方式
    """
    # 大端在前
    BIG_ENDIAN = 0
    # 小端在前
    LITTLE_ENDIAN = 1

class Packet(Endian):
    """
    封装的协议包类，支持二进制数据读写
    """
    def __init__(self, buf=None):
        """
        创建一个协议包
        :param buf:
        """
        # 二进制python3中用BytesIO ， py2中可以用StringIO代替
        self.__buf = BytesIO()
        # 传入参数进行判断 支持 str ，bytes 和 Packet自身
        if isinstance(buf, bytes):
            self.__buf.write(buf)
        elif isinstance(buf, str):
            self.__buf.write(buf.encode())
        elif isinstance(buf, Packet):
            self.__buf.write(buf.getvalue())
        elif buf is None:
            pass
        else:
            raise TypeError("buf type is not support")
        # 对齐方式
        self.endian = self.BIG_ENDIAN
        # 当前位置
        self.position = 0

    def readShort(self):
        """ """
        fmt = "%sh" % self._isEndian()
        res = struct.unpack(fmt, self._readbuf(2))
        return res[0]

    def readUnsignedShort(self):
        """"""
        fmt = "%sH" % self._isEndian()
        res = struct.unpack(fmt, self._readbuf(2))
        return res[0]

    def readInt(self):
        """ """
        fmt = "%si" % self._isEndian()
        res = struct.unpack(fmt, self._readbuf(4))
        return res[0]

    def readUnsignedInt(self):
        """ """
        fmt = "%sI" % self._isEndian()
        res = struct.unpack(fmt, self._readbuf(4))
        return res[0]

    def readFloat(self):
        """ """
        fmt = "%sf" % self._isEndian()
        res = struct.unpack(fmt, self._readbuf(4))
        return res[0]

    def readDouble(self):
        """ """
        fmt = "%sd" % self._isEndian()
        res = struct.unpack(fmt, self._readbuf(8))
        return res[0]

    def readUTFBytes(self, nlen):
        """ """
        fmt = "%ss" % nlen
        res = struct.unpack(fmt, self._readbuf(nlen))
        return res[0]

    def readMulitBytes(self,nlen):
        """"""
        return self._readbuf(nlen)

    def readString(self):
        """ """
        nlen = self.readUnsignedShort()
        if nlen > 0:
            return self.readUTFBytes(nlen)
        return ""

    def readByte(self):
        """ """
        fmt = "%sb" % self._isEndian()
        res = struct.unpack(fmt, self._readbuf(1))
        return res[0]

    def readUnsignedByte(self):
        """ """
        fmt = "%sB" % self._isEndian()
        res = struct.unpack(fmt, self._readbuf(1))
        return res[0]

    def writeShort(self, value):
        """ """
        fmt = "%sh" % self._isEndian()
        self._addbuf(struct.pack(fmt, value))

    def writeUnsignedShort(self, value):
        """ """
        fmt = "%sH" % self._isEndian()
        self._addbuf(struct.pack(fmt, value))

    def writeInt(self, value):
        """ """
        fmt = "%si" % self._isEndian()
        self._addbuf(struct.pack(fmt, value))

    def writeUnsignedInt(self, value):
        """ """
        fmt = "%sI" % self._isEndian()
        self._addbuf(struct.pack(fmt, value))

    def writeFloat(self,value):
        """"""
        fmt = "%sf" % self._isEndian()
        self._addbuf(struct.pack(fmt, value))

    def writeDouble(self, value):
        """ """
        fmt = "%sd" % self._isEndian()
        self._addbuf(struct.pack(fmt, value))

    def writeUTFBytes(self,value):
        """ """
        if isinstance(value,str):
            value = value.encode()
        fmt = "%ss" % (len(value))
        self._addbuf(struct.pack(fmt, value))

    def writeMulitBytes(self, value):
        """"""
        if isinstance(value,str):
            value = value.encode()
        elif isinstance(value, Packet):
            value = value.getvalue()
        self._addbuf(value)

    def writeString(self, value):
        """"""
        nlen = len(value)
        self.writeUnsignedShort(nlen)
        if nlen > 0:
            self.writeUTFBytes(value)

    def writeByte(self, value):
        """"""
        fmt = "%sb" % self._isEndian()
        self._addbuf(struct.pack(fmt, value))

    def writeUnsignedByte(self, value):
        """"""
        fmt = "%sB" % self._isEndian()
        self._addbuf(struct.pack(fmt, value))

    def getvalue(self):
        """ """
        return self.__buf.getvalue()

    def length(self):
        """ """
        old_pos = self.__buf.tell()
        self.__buf.seek(0,2)
        nlen = self.__buf.tell()
        self.__buf.seek(old_pos)
        return nlen

    def clear(self):
        """"""
        try:
            self.__buf.close()
            self.__buf = BytesIO()
            self.position = 0
        except Exception as e:
            print(e)

    def reset(self,data):
        """"""
        self.clear()
        self.writeMulitBytes(data)
        self.position = 0

    def _addbuf(self, value):
        """ """
        old_pos = self.__buf.tell()
        if old_pos != self.position:
            self.__buf.seek(self.position)
        self.__buf.write(value)
        self.position = self.__buf.tell()

    def _readbuf(self, nlen):
        """ """
        old_pos = self.__buf.tell()
        if old_pos != self.position:
            self.__buf.seek(self.position)
        buf = self.__buf.read(nlen)
        self.position += nlen
        return buf

    def _isEndian(self):
        """
        返回大小端的标记
        :return:
        """
        if self.endian == self.BIG_ENDIAN:
            return ">"
        else:
            return ""


if __name__ == "__main__":
    data = Packet('')
    data.writeShort(2)
    data.writeShort(1)
    data.writeShort(len("jack"))
    data.writeUTFBytes("jack")

    data.writeShort(len("e10adc3949ba59abbe56e057f20f883e"))
    data.writeUTFBytes("e10adc3949ba59abbe56e057f20f883e")
    data.endian = Endian.LITTLE_ENDIAN
    data.position = 0
    data.writeShort(data.length())
    print(binascii.hexlify(data.getvalue()))
