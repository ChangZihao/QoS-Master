import QoSPolicy.simple as simple
import QoSPolicy.MAGI.magi as magi
import monitor
import globalInfo
from multiprocessing import Process, Value

# 策略注册点，name：Run， name需要与config.json中的策略名对应，Run是策略的入口函数。
ruleMap = {
    "simple": simple.Run,
    "magi": magi.Run
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

    # 策略的启动函数
    def run(self, node, pod):
        for po in self.policy:
            runFlag = Value('i', 0)
            proc = Process(target=ruleMap[po], args=(
                self, node, pod, monitor.Monitor(node), runFlag,))
            globalInfo.AddPolicyProc(pod, {"flag": runFlag, "proc": proc})
            proc.start()
