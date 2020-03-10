import rule
from multiprocessing import Manager


class Data:
   
    monitorData = Manager().dict()  # 生成一个可在多个进程之间传递和共享的字典
    rules = {}          # key: rule.name. value: rule
    registerInfo = {}   # key: pod, value:[node, app, pod]
    # monitorData = {}    # key: node, value:metric_family(prom)
    nodes = []
    monitorThread = {}  # key: node, value thread
    monitorInterval = 0.5


def DeleteMonitorThread(node):
    if node in Data.monitorThread:
        Data.monitorThread.pop(node)


def GetAllMonitorThreads() -> {}:
    return Data.monitorThread


def AddMonitorThread(node, thread):
    Data.monitorThread[node] = thread


def DeleteMonitorData(node):
    if node in Data.monitorData:
        Data.monitorData.pop(node)


def GetAllMonitorData():
    return Data.monitorData


def AddMonitorData(node, data):
    Data.monitorData[node] = data


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
