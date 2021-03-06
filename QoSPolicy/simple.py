import logger

log = logger.create_logger("policy.simple")


def Run(rule, node, pod, monitor, flag):
    i = 5
    while i > 0:
        if flag.value == 0:
            log.info("simple: %s %s", node, pod)
            # res = monitor.getData(rule.input, [pod])
            # get monitor data
            # log.info("Simple get %s: %f", res[0].name, res[0].value)
            # log.info("Simple get %s: %f", res[1].name, res[1].value)
            # Do action
            if rule.appname.find("markdown") != -1:
                log.info("markdown: Alloc llc: %s", monitor.action(pod, "llc", 2))
                log.info("markdown: Alloc cpushare: %s", monitor.action(pod, "cpu_share", 25))
            elif rule.appname.find("sentiment") != -1:
                log.info("sentiment: Alloc llc: %s", monitor.action(pod, "llc", 2))
                log.info("sentiment: Alloc cpushare: %s", monitor.action(pod, "cpu_share", 25))
            elif rule.appname.find("ocr") != -1:
                log.info("ocr: Alloc llc: %s", monitor.action(pod, "llc", 10))
                log.info("ocr: Alloc cpushare: %s", monitor.action(pod, "cpu_share", 200))
            # stop
            monitor.stop(pod)

        elif flag.value == 1:
            log.info("Simple policy Ready to stop!")
            flag.value = 2
            return
