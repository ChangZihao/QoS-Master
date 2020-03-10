import time
import logger

log = logger.create_logger("flask.app")


def simple(rule, node, pod, monitor):
    i = 3
    while i > 0:
        log.info("simple: %s %s", node, pod)
        res = monitor.getData(rule.input, [pod])
        cpushare = int(float(res[0].value)) + 25
        log.info("simple cpu share value is: %s", cpushare)
        log.info(monitor.action(pod, rule.output[0], cpushare))
        time.sleep(5)
        i = i - 1
