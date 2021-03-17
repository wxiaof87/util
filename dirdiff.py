import os
import sys
import hashlib
import concurrent.futures
import queue
import time
import threading
import logging
import traceback
from collections import defaultdict

# store all file path into fileSet
def listAllFiles(root, path, fileSet):
    if os.path.isdir(path):
        for subPath in os.listdir(path):
            listAllFiles(root, path + "/" + subPath, fileSet)
    else:
        fileSet.add(path[len(root):])
        #print(path)


def doDiff(leftDir, rightDir):
    print("leftDir: {}, rightDir: {}".format(leftDir, rightDir))
    leftFileSet, rightFileSet = set([]), set([])
    listAllFiles(leftDir, leftDir, leftFileSet)
    listAllFiles(rightDir, rightDir, rightFileSet)

    # print(leftFileSet)
    common = leftFileSet & rightFileSet
    leftOnly = leftFileSet - common
    righOnly = rightFileSet - common
    print('leftOnly', leftOnly)
    print('rightOnly', righOnly)
    # print('common', common)
    ignoreFileSet = set([])
    # ignoreFileSet.add('xxx')
    for fileName in common:
        if fileName in ignoreFileSet:
            print('skip ' + fileName)
            continue
        leftFilePath = leftDir + fileName
        rightFilePath = rightDir + fileName
        cmd = ' '.join(['diff', leftFilePath, rightFilePath])
        result = os.system(cmd)
        if(result > 0):
            print("^^^" + fileName + "^^^")


if __name__ == '__main__':
    leftDir = sys.argv[1]
    rightDir = sys.argv[2]
    doDiff(leftDir, rightDir)

