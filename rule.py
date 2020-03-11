import policy.simple
import monitor
import globalInfo
from multiprocessing import Process, Value

ruleMap = {
    "simple": policy.simple.simple
}


class Rule:
    def __init__(self, appname, qosClass, sla, policy, input, output):
        self.appname = appname
        self.qosClass = qosClass
        if sla is not None:
            self.sla = {**sla}
        self.policy = []
        if policy is not None:
            self.policy.extend(policy)
        self.input = []
        if input is not None:
            self.input.extend(input)
        self.output = []
        if output is not None:
            self.output.extend(output)

    def run(self, node, pod):
        for po in self.policy:
            runFlag = Value('i', 0)
            proc = Process(target=ruleMap[po], args=(
                self, node, pod, monitor.Monitor(node), runFlag,))
            globalInfo.AddPolicyProc(pod, {"flag": runFlag, "proc": proc})
            proc.start()
