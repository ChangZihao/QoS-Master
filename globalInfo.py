class Data:
    rules = {}
    registerInfo = {}
    monitorData = {}
    nodes = []
    monitorThread = {}
    monitorInterval = 0.5


def GetAllMonitorThreads():
    return Data.monitorThread


def SetMonitorThread(node, thread):
    Data.monitorThread[node] = thread


def GetAllMonitorData():
    return Data.monitorData


def SetMonitorData(node, data):
    Data.monitorData[node] = data


def SetNodes(nodes):
    Data.nodes = nodes


def GetNodes():
    return Data.nodes


def SetRules(rules):
    Data.rules = rules


def GetRule(app):
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
