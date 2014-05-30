# -*- coding: utf-8 -*-
import zipfile
import os.path
import os

__all__ = ['create_zip', 'extract_zip']

class ZFile(object):

    def __init__(self, filename, mode='r', basedir=''):
        self.filename = filename
        self.mode = mode
        if self.mode in ('w', 'a'):
            self.zfile = zipfile.ZipFile(filename, self.mode, compression=zipfile.ZIP_DEFLATED)
        else:
            self.zfile = zipfile.ZipFile(filename, self.mode)
        self.basedir = basedir
        if not self.basedir:
            self.basedir = os.path.dirname(filename)

    def addfile(self, path, arcname=None):
        path = path.replace('\\', '/')
        if not arcname:
            if path.startswith(self.basedir):
                arcname = path[len(self.basedir):]
            else:
                arcname = path.split('/')[-1]
        self.zfile.write(path, arcname)

    def addfiles(self, paths):
        for path in paths:
            if isinstance(path, tuple) or isinstance(path, list):
                self.addfile(*path)
            else:
                self.addfile(path)

    def close(self):
        self.zfile.close()

    def extract_to(self, path):
        for p in self.zfile.namelist():
            self.extract(p, path)

    def extract(self, filename, path):
        if not filename.endswith('/'):
            f = os.path.join(path, filename)
            dir = os.path.dirname(f)
            if not os.path.exists(dir):
                os.makedirs(dir)
            file(f, 'wb').write(self.zfile.read(filename))

def create_zip(zfile, files):
    z = ZFile(zfile, 'w')
    z.addfiles(files)
    z.close()

def extract_zip(zfile, path):
    z = ZFile(zfile)
    z.extract_to(path)
    z.close()
