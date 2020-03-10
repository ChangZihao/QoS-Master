import threading
import globalInfo
import requests
import time
import logging
from prometheus_client.parser import text_string_to_metric_families

logger = logging.getLogger('flask.app')


class MonitorThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, node):
        super(MonitorThread, self).__init__()
        self._stop_event = threading.Event()
        self.node = node

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        retry = 0
        while True:
            try:
                response = requests.get(
                    "http://{}:9001/metrics".format(self.node)).content.decode("utf-8")

            except:
                retry = retry + 1
                logger.error(
                    "Fail to get monitor data from http://{}:9001/metrics. Retry {}".format(
                        self.node, retry))
                if retry >= 3:
                    logger.error(
                    "Fail to get monitor data from http://{}:9001/metrics. Retry over!".format(
                        self.node))
                    globalInfo.DeleteMonitorThread(self.node)
                    globalInfo.DeleteMonitorData(self.node)
                    break
                
            else:
                metrics = text_string_to_metric_families(response)
                globalInfo.AddMonitorData(self.node, metrics)
                print("after store", globalInfo.GetAllMonitorData())
                time.sleep(globalInfo.Data.monitorInterval)


def startMonitor():
    threads = globalInfo.GetAllMonitorThreads()
    for node in globalInfo.GetNodes():
        if node not in threads:
            t = MonitorThread(node)
            threads[node] = t
            t.start()
