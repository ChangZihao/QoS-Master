# class Simple:
#     def __init__(self, node, pod):
#         self.node = node
#         self.pod = pod

#     def simple(self, node, pod):
#         return node, pod, "action"
import globalInfo
import time


def simple(rule, node, pod, data):
    i = 5
    while i > 0:
        print("simple:", node, pod)
        print("simple", data['0.0.0.0'])
        # if node in data.keys():
        #     print("self", rule.name)
        #     return node, pod, "action"
        # else:
        #     # globalInfo.GetAllRegister().pop(pod)
        #     print("node data!!!!")
        time.sleep(2)
        i = i - 1
