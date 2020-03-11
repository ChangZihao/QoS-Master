import logging
import json
import globalInfo
import time
import threading
import rule as config

logger = logging.getLogger('flask.app')


def register(node, app, pod):
    if globalInfo.GetRegister(pod) is None:
        globalInfo.AddRegister([node, app, pod])
        rule = globalInfo.GetRule(app)
        if rule is None:
            logger.info(
                "Register failed, no matching rule: <%s, %s, %s>", node, app, pod)
            return False
        else:
            rule.run(node, pod)
            logger.info("Register success: <%s, %s, %s>", node, app, pod)
            return True

    else:
        logger.info("Register Info already exit: <%s, %s, %s>", node, app, pod)
        return False


def stop(pod):
    globalInfo.DeletRegister(pod)
    proc = globalInfo.GetPolicyProc(pod)
    if proc is not None:
        proc["flag"].value = 1
        threading.Thread(target=procClean, args=(pod,)).start()
        return True
    else:
        logger.warning("Pod does not exit: %s", pod)
        return False


def json2RuleList(d):
    if "appname" in d:
        rule = config.Rule(d["appname"], d["class"], d["sla"],
                           d["policy"], d["input"], d["output"])
        return rule
    elif "rules" in d:
        return {"rules": {r.appname: r for r in d["rules"]}}
    else:
        return {**d}


def loadConfig():
    with open("config.json", "r") as configFile:
        config = json.load(configFile, object_hook=json2RuleList)
        globalInfo.SetRules(config["rules"])
    return True


def procClean(pod):
    proc = globalInfo.GetPolicyProc(pod)
    for _ in range(0, 3):
        time.sleep(5)
        if proc["flag"].value == 2:
            proc["proc"].close()
            logger.info("Clean policy proc of %s", pod)
            return

    logger.info("Clean policy violent proc of %s", pod)
    proc["proc"].terminate()
    time.sleep(5)
    proc["proc"].close()
