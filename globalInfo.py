import rule


class Data:
    rules = {}          # key: rule.name. value: rule
    registerInfo = {}   # key: pod, value:[node, app, pod]


def SetNodes(nodes):
    Data.nodes = nodes


def GetNodes() -> []:
    return Data.nodes


def SetRules(rules):
    Data.rules = rules


def GetRule(app) -> rule.Rule:
    if app in Data.rules:
        return Data.rules[app]
    return None


def GetAllRules():
    return Data.rules


def AddRegister(list):
    Data.registerInfo[list[2]] = list


def DeletRegister(pod):
    return Data.registerInfo.pop(pod)


def GetRegister(pod):
    if pod in Data.registerInfo.keys():
        return Data.registerInfo[pod]
    else:
        return None


def GetAllRegister():
    return Data.registerInfo
