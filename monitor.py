import requests
import logging
import logic
from prometheus_client.parser import text_string_to_metric_families

logger = logging.getLogger('flask.app')

# Monitor是QoS-Master为策略的提供的数据交互和资源调控接口，可以提供节点上的实时数据监控和资源调控操作。
class Monitor:
    def __init__(self, node):
        self.node = node
        self.pods = {}

    # 获取节点监控数据，apps是list [app1, app2]
    def getData(self, apps):
        self.pods = {}
        retVal = {}
        retry = 0
        while True:
            try:
                response = requests.get(
                    "http://{}:9001/metrics".format(self.node)).content.decode("utf-8")

            except:
                retry = retry + 1
                logger.error(
                    "Fail to get monitor data from http://{}:9001/metrics. Retry {}".format(self.node, retry))
                if retry >= 3:
                    logger.error(
                        "Fail to get monitor data from http://{}:9001/metrics. Retry over!".format(self.node))
                    return retVal

            else:
                familys = text_string_to_metric_families(response)
                for family in familys:
                    for sample in family.samples:
                        if sample.labels["app"] not in self.pods:
                            self.pods[sample.labels["app"]] = set()
                        self.pods[sample.labels["app"]].add(
                            sample.labels["pod"])

                        if sample.labels["app"] in apps:
                            if sample.labels["app"] not in retVal:
                                retVal[sample.labels["app"]] = {}
                            retVal[sample.labels["app"]
                                   ][sample.name] = sample.value
                return retVal

    # 利用应用名获取应用对应的pod id
    def getPodNameByapp(self, app):
        if app in self.pods:
            return self.pods[app]
        return []

    # 下发资源调控指令
    def action(self, pod, resourceType, value):
        value = int(value)
        payload = {"pod": pod, "resourceType": resourceType, "value": value}
        retry = 0
        while True:
            try:
                response = requests.get(
                    "http://{}:9001/control".format(self.node), params=payload).content.decode("utf-8")

            except:
                retry = retry + 1
                logger.error(
                    "Fail to send action to http://{}:9001/control?pod={}&resourceType={}&value={}. Retry {}".format(self.node, pod, resourceType, value, retry))
                if retry >= 3:
                    logger.error(
                        "Fail to send action to http://{}:9001/control?pod={}&resourceType={}&value={}. Retry over!".format(self.node, pod, resourceType, value))
                    return False

            else:
                logger.info(
                    "Send action to http://{}:9001/control?pod={}&resourceType={}&value={}. Response:{}".format(self.node, pod, resourceType, value, response))
                return True

    def stop(self, pod):
        logic.stop(pod)
