class Rule:
    def __init__(self, name, qosClass, policy, input, output):
        self.name = name
        self.qosClass = qosClass
        self.policy = []
        self.policy.extend(policy)
        self.input = []
        self.input.extend(input)
        self.output = []
        self.output.extend(output)


def json2RuleList(d):
    if "name" in d:
        rule = Rule(d["name"], d["class"], d["policy"],
                    d["input"], d["output"])
        return rule
    if "rules" in d:
        return {r.name: r for r in d["rules"]}
