import policy.simple

ruleMap = {
    "simple": policy.simple.simple
}


class Rule:
    process = {}

    def __init__(self, name, qosClass, sla, policy, input, output):
        self.name = name
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
        # if node not in globalInfo.GetAllMonitorThreads().keys():
        #     t = monitor.MonitorThread(node)
        #     globalInfo.SetMonitorThread(node, t)
        #     t.start()
        print(ruleMap[self.policy[0]](node, pod))

