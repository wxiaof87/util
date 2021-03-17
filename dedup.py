import os
import hashlib
import concurrent.futures
import queue
import time
import threading
import logging
import traceback
from collections import defaultdict


def process(paths):
    # TODO: add file type filtering
    result = []
    for path in paths:
        key = None
        mtime = None
        try:
            mtime = int(os.path.getmtime(path))  # last modification time in seconds
            size = os.path.getsize(path)  # size in bytes
            maxBytes = 64 * 1024 * 1024  # max bytes to read
            # raise Exception('exception') # for test
            with open(path, 'rb') as f:
                content = f.read(maxBytes)
                key = hashlib.md5(content).hexdigest()
                key += "_" + str(size)
        except Exception as e:
            logging.error("failed to process " + path + "\n" + traceback.format_exc())
        result.append((key, path, mtime))
    return result


class Producer(threading.Thread):
    def __init__(self, q, paths):
        threading.Thread.__init__(self)
        self.executor = concurrent.futures.ProcessPoolExecutor()
        # self.executor = concurrent.futures.ThreadPoolExecutor()
        self.q = q
        self.maxQueueSize = 128
        self.paths = paths
        self.logger = logging.getLogger(self.__class__.__name__)
        self.buffer = []  # submit task by batch
        self.bufferSize = 16

    def run(self) -> None:
        self.logger.info("entering producer thread")
        for path in self.paths:
            self.generateTask(path)
        if len(self.buffer) > 0:
            self.flushTasks()
        self.logger.info("exiting producer thread")

    def generateTask(self, path):
        if os.path.isdir(path):
            # self.logger.info("generate task for " + path)
            for subPath in os.listdir(path):
                self.generateTask(path + "/" + subPath)
        else:
            # TODO: submit job by mini-batch
            while self.q.qsize() > self.maxQueueSize:
                self.logger.info('pause! qsize: ' + str(self.q.qsize()))
                time.sleep(1)
            self.buffer.append(path)

            if len(self.buffer) > self.bufferSize:
                self.flushTasks()
            # TODO: pause job submission if too many pending tasks

    def flushTasks(self):
        future = self.executor.submit(process, self.buffer)
        self.q.put(future)
        self.buffer = []

    def shutdown(self):
        self.logger.info("wait for producer")
        self.join()
        self.logger.info("wait for executor")
        self.executor.shutdown()


class Consumer(threading.Thread):
    def __init__(self, q, summaryFileName):
        threading.Thread.__init__(self)
        self.q = q
        self.logger = logging.getLogger(self.__class__.__name__)
        self.key2Files = defaultdict(list)
        self.summaryFileName = summaryFileName

    def run(self) -> None:
        self.logger.info('entering consumer thread')
        cnt = 0
        while True:
            # self.logger.info('consume one result batch')
            future = self.q.get()
            self.q.task_done()
            if future is None:  # shutdown flag
                break
            result = future.result()

            #TODO: report progress here
            for key, path, mtime in result:
                # print(' '.join(item))
                if key is None:
                    self.logger.error("can't process " + path)
                else:
                    self.key2Files[key].append((path, mtime))
                    cnt += 1
                    if cnt % 100 == 0:
                        self.logger.info("progress: {}".format(cnt))
        self.writeSummary()
        self.logger.info('exiting consumer thread')

    def writeSummary(self):
        with open(self.summaryFileName, 'w') as f:
            for key, pathList in sorted(self.key2Files.items(), key=lambda item: len(item[1])):
                pathList.sort(key=lambda x: x[1])  # order by time
                orderedPaths = [path for path, mtime in pathList]  # remove mtime
                f.write(key + "\t" + ','.join(orderedPaths) + "\n")

    def shutdown(self):
        self.logger.info("wait for consumer")
        self.q.put(None)
        self.q.join()
        self.join()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    logger = logging.getLogger(__file__)
    logger.info('start')
    startTime = time.time()
    inputPaths = ['~/Pictures']

    summaryFileName = "summary.txt"

    q = queue.Queue()
    producer = Producer(q, inputPaths)
    consumer = Consumer(q, summaryFileName)

    producer.start()
    consumer.start()

    producer.shutdown()
    consumer.shutdown()

    endTime = time.time()
    logger.info('total time used: ' + str(endTime - startTime))
    logger.info('exit')
