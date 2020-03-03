import logging
import json
import globalInfo
import config

logger = logging.getLogger('flask.app')


def register(node, app, pod):
    if globalInfo.GetRegister(pod) is None:
        globalInfo.AddRegister([node, app, pod])
        logger.info("Register success: <%s, %s, %s>", node, app, pod)
        return True
    else:
        logger.info("Register Info already exit: <%s, %s, %s>", node, app, pod)
        return False


def stop():
    print("changzihao")
    return 'ok'


def loadConfig():
    with open("config.json", "r") as configFile:
        rules = json.load(configFile, object_hook=config.json2RuleList)
        globalInfo.SetRules(rules)
    return True
