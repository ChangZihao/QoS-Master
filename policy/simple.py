import time
import logger

log = logger.create_logger("policy.simple")


def simple(rule, node, pod, monitor, flag):
    i = 5
    while i > 0:
        if flag.value == 0:
            log.info("simple: %s %s", node, pod)
            res = monitor.getData(rule.input, [pod])
            cpushare = int(float(res[0].value)) + 25
            log.info("simple cpu share value is: %s", cpushare)
            # log.info(monitor.action(pod, rule.output[0], cpushare))
            time.sleep(10)
            i = i - 1

        elif flag.value == 1:
            log.info("Simple policy Ready to stop!")
            flag.value = 2
            # return

        else:
            continue
