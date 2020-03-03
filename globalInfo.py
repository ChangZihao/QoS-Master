class Data:
    rules = {}
    registerInfo = {}


def SetRules(rules):
    Data.rules = rules


def GetRules():
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
