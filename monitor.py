import threading
import globalInfo
import requests
import time
from prometheus_client.parser import text_string_to_metric_families


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
        while True:
            response = requests.get(
                "http://{}:9001/metrics".format(self.node)).content.decode("utf-8")
            metrics = text_string_to_metric_families(response)
            globalInfo.SetMonitorData(self.node, metrics)
            time.sleep(globalInfo.Data.monitorInterval)
            break


def startMonitor():
    threads = globalInfo.GetAllMonitorThreads()
    for node in globalInfo.GetNodes():
        if node not in threads:
            t = MonitorThread(node)
            threads[node] = t
            t.start()
