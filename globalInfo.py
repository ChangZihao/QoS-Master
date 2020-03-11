import rule


class Data:
    rules = {}          # key: rule.name. value: rule
    registerInfo = {}   # key: pod, value:[node, app, pod]

    # key: pod, value:{flag: multiprocessing.Value.int, proc: multiprocessing.Process} mutiprocessing Value(bool)
    # 0 -> runing; 1 -> tell policy to stop; 3 -> policy stopped, waitting to be recycle
    policyProc = {}


def GetPolicyProc(pod):
    if pod in Data.policyProc:
        return Data.policyProc[pod]
    else:
        return None


def AddPolicyProc(pod, proc):
    Data.policyProc[pod] = proc


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
    if pod in Data.registerInfo:
        Data.registerInfo.pop(pod)


def GetRegister(pod):
    if pod in Data.registerInfo.keys():
        return Data.registerInfo[pod]
    else:
        return None


def GetAllRegister():
    return Data.registerInfo
