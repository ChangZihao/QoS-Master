import logging
import json
import globalInfo
import rule as config

logger = logging.getLogger('flask.app')


def register(node, app, pod):
    if globalInfo.GetRegister(pod) is None:
        globalInfo.AddRegister([node, app, pod])
        rule = globalInfo.GetRule(app)
        if rule is None:
            logger.info("Register failed, no matching rule: <%s, %s, %s>", node, app, pod)
            return False
        else:
            rule.run(node, pod)
            logger.info("Register success: <%s, %s, %s>", node, app, pod)
            return True

    else:
        logger.info("Register Info already exit: <%s, %s, %s>", node, app, pod)
        return False


def stop():
    print("changzihao")
    return 'ok'


def json2RuleList(d):
    if "appname" in d:
        rule = config.Rule(d["appname"], d["class"], d["sla"],
                    d["policy"], d["input"], d["output"])
        return rule
    elif "rules" in d:
        return {"rules": {r.appname: r for r in d["rules"]}, "nodes": d["nodes"]}
    else:
        return {**d}


def loadConfig():
    with open("config.json", "r") as configFile:
        config = json.load(configFile, object_hook=json2RuleList)
        globalInfo.SetRules(config["rules"])
        globalInfo.SetNodes(config["nodes"])
    return True
