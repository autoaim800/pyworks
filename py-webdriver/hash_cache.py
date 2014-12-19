import os
import sys
import hashlib

class HashFileCache:

    def __init__(self, workDir):
        self.cacheDir = os.path.abspath(workDir)
        if not os.path.exists(self.cacheDir):
            os.mkdir(self.cacheDir)
        self.__hashFp = dict()

    def calcDig(self, raw):
        m = hashlib.sha1(raw)
        return m.hexdigest()

    def _buildFp(self, name):

        if name in self.__hashFp:
            return self.__hashFp[name]

        dig = self.calcDig(name)
        p1 = dig[0:2]
        p2 = dig[2:]
        d1 = os.path.join(self.cacheDir, p1)
        if not os.path.exists(d1):
            os.mkdir(d1)
        fp = os.path.join(d1, p2)
        self.__hashFp[name] = fp
        return fp

    def store(self, name, content):
        fp = self._buildFp(name)
        self.writef(fp, content)

    def exists(self, name):
        fp = self._buildFp(name)
        return os.path.exists(fp)

    def fetch(self, name):
        fp = self._buildFp(name)
        print(fp)
        if os.path.exists(fp):
            return self.__readFile(fp)
        return None

    @staticmethod
    def __readFile(fp):
        with open(fp, "r") as f:
            return f.read()
        return None
    @staticmethod
    def writef(fp, content):
        with open(fp, "w") as f:
            f.write(content)

class PlainFileCache(HashFileCache):
    def __init__(self, workDir):
        HashFileCache.__init__(self, workDir)

    def calcDig(self, name):
        return name
