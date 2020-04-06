import json
import random
import time
import QoSPolicy.MAGI.policy as po
import os


class CpuController:
    def __init__(self, controll_config, samples, en_data, en_train, en_auto_sla, accuracy, sleep_interval, monitor):
        print("CpuController:init")
        self.enable_data_driven = en_data
        self.enable_training = en_train
        self.enable_auto_sla = en_auto_sla
        self.sleep_interval = sleep_interval
        self.allGroups = samples  # ["app1","app2"]
        self.monitor = monitor
        self.controlConfig = controll_config
        self.slas = {}

        self.policies = {}
        for g in samples:
            self.policies[g] = po.Policy(
                g, self.allGroups, controll_config, accuracy, self.monitor)
            self.slas[g] = controll_config[g]["SLA"]["ipc"]

        self.currentInfo = {}

        self.throttled_group = set()

        self.relax_count = 0

        # filename_cpuusage = 'cpuUsage.txt'
        # if os.path.exists(filename_cpuusage):
        #     os.remove(filename_cpuusage)
        # get MAGI's pid
        self.pid_magi = os.getpid()
        # print()

    # try to add the groups who break SLA

    def try_to_add_sample(self):
        print("CpuController:try_to_add_sample")
        print("allgroups: ", self.allGroups)
        tmp_info = None
        check_live = 0
        while tmp_info is None:
            if(check_live == 10):
                print("Err: some app may exit!")
                return -1
            check_live += 1
            tmp_info = tmp_info = self.monitor.getData(self.allGroups)
        self.currentInfo = tmp_info
        # print("    get currentInfo" + str(self.currentInfo))
        samples = []
        # print("    try to add sample, currentInfo keys:" + str(self.currentInfo.keys()))
        print(self.currentInfo)
        for group in self.currentInfo.keys():
            print("    " + group + ": current ipc:" + str(self.currentInfo[group]["ipc_metric"]) + " slas: " + str(
                self.slas[group]) + " controlConfig:" + str(self.controlConfig[group]["SLA"]["ipc"]))
            # print(str(group) + ": current ipc:" + str(float(self.currentInfo[group]["ipc"])) + "slas:" + str(self.slas[group]["ipc"]))
            # now the sla depends on ipc=instructions/cycles
            if float(self.currentInfo[group]["ipc_metric"]) < self.slas[group]:
                samples.append(group)
            if self.enable_auto_sla:
                self.slas[group] = self.slas[group] * 0.4 + float(
                    self.currentInfo[group]["ipc_metric"]) * 0.1 + float(self.controlConfig[group]["SLA"]["ipc"]) * 0.5
        # print("can return samples")
        print("    " + str(samples) + " have been add to samples\n")
        return samples

    def run(self):
        print("CpuController:run")
        while True:
            if self.sleep_interval > 0:
                time.sleep(self.sleep_interval)

            # try_to_add_sample will also collect the current info of all the groups
            sample = self.try_to_add_sample()
            if sample == -1:
                return -1
            # tmp_data = {}
            for g in self.allGroups:  # allGroup should <= self.policies.keys()y
                self.policies[g].with_run(
                    self.currentInfo, self.enable_training)
            #     print("    current ipc: ", self.currentInfo[g]["ipc"])
            #     print("    current cpu quota: ", rM.get_cfs_quota(g))
            #     print("    current llm: ",
            #           self.llcM.cosLlcNum(llcM.groupCOS[g]))

            #     tmp_data[g + "_ipc"] = self.currentInfo[g]["ipc"]
            #     tmp_data[g + "_cpu"] = rM.get_cfs_quota(g)
            #     tmp_data[g + "_llc"] = self.llcM.cosLlcNum(llcM.groupCOS[g])
            #     tmp_data[g + "_sla"] = self.slas[g]
            # experi_data.append(tmp_data)
            self.check_cpu(sample)
            # print("round in a period is:" + str(total_round))
            # if total_round == STORE_PERIOD:
            #     # timeNow = time.asctime(time.localtime(time.time()))
            #     dataF = open(po.es.SAVE_PATH + "data_for_plot.csv", 'a')
            #     # json.dump(experi_data, dataF)
            #     dict_w = csv.DictWriter(dataF, headers)
            #     dict_w.writerows(experi_data)
            #     experi_data.clear()
            #     dataF.close()
            #     total_round = 0
            # total_round += 1

            # get MAGI CPU q
            # cpu_magi = psutil.cpu_percent(interval=1, percpu=False)

            # cpu_apps = 0.0
            # for g in self.allGroups:
            #     cpu_apps += rM.get_cpu_usage(g)

            # cpu_sum = cpu_magi + cpu_apps

            # f1 = open('cpuUsage.txt', 'a')
            # # mgin apps total
            # f1.write('%8s %8s %8s\n'
            #          % ('%.1f' % cpu_magi, '%.1f' % cpu_apps, '%.1f' % cpu_sum))
            # f1.close()
            print("-----------------------------------")

# select the least-ipc group in sample
    def select_low_ipc_group(self, sample):
        print("CpuController:select_low_ipc_group")
        if len(sample) == 0:
            return None
        '''
        res = ''
        minpA = 999
        for g in sample:
            pids = rM.cgroup.getCgroupPids(g)
            pA = 0.0
            for p in pids:
                pA = pA + rM.cat.getIpc(int(p))
            pA = pA / float(len(pids))
            if minpA >= pA:
                minpA = pA
                res = g
        return res
        '''
        # print("select_low_ipc_group")
        least_ipc = 9999.9
        least_group = ""
        for group in sample:
            tmpIpc = 0.0
            try:
                tmpIpc = float(self.currentInfo[group]["ipc"])
            except:
                print(self.currentInfo[group])
            if tmpIpc < least_ipc:
                least_ipc = tmpIpc
                least_group = group
        # print("    current low icp is: " + least_group)
        return least_group

    def check_cpu(self, sample):
        print("CpuController:check_cpu")
        print("    sample:" + str(sample))
        # sample is a list filled with groups needed to be watched
        group = self.select_low_ipc_group(sample)
        print("    select low ipc group:" + str(group))
        if group is not None:
            self.start_cpu_throttle_analyst(group)
        elif self.relax_count >= 2:
            self.relax_count = 0
            self.start_cpu_relax_analyst()
        else:
            self.relax_count += 1
        print()

    def start_cpu_relax_analyst(self):
        print("CpuController:start_cpu_relax_analyst")
        t = ""
        if len(self.throttled_group) == 0:
            t = random.choice(self.allGroups)
            print("    random " + t + " has been selected")
        else:
            t = self.throttled_group.pop()
            print("    throttled_group " + t + " has been selected")
        if self.controlConfig[t]["maximum_setups"]["cpu_share"] > self.currentInfo[t]["cpu_share"]:
            for pod in self.monitor.getPodNameByapp(t):
                self.monitor.action(
                    pod, "cpu_share", self.currentInfo[t]["cpu_share"] + 25)
        if self.controlConfig[t]["maximum_setups"]["llc"] > self.currentInfo[t]["llc_capacity"] and self.currentInfo[t]["llc_capacity"] > 0:
            for pod in self.monitor.getPodNameByapp(t):
                self.monitor.action(
                    pod, "llc", self.currentInfo[t]["llc_capacity"] + 1)
        return 0

    def start_cpu_throttle_analyst(self, group):
        policy = self.policies[group]
        print("CpuController:start_cpu_throttle_anaylyst")
        # if self.enable_data_driven and policy.estimator.workable():
        if self.enable_data_driven:
            # gqb
            if policy.throttle_target_select_setup(self.throttled_group, self.slas[group]) == -1:
                print("start to run rule model!")
                if policy.rule_update(self.throttled_group) == -1:
                    print("Err: toplev_update Fail")
                    return -1
        else:
            if policy.rule_update(self.throttled_group) == -1:
                print("Err: toplev_update Fail")
                return -1
        print()
        return 0


def Run(rule, node, pod, monitor, flag):
    controll_config = json.loads(open("QoSPolicy/MAGI/magiConfig.json", 'r').read())
    print("start magi for pod %s", pod)
    print(controll_config)
    # here samples are like : ["app1","app2"]
    c = CpuController(controll_config, [
                      "markdown2html-knmwk", "ocr-image-lgplq", "sentiment-analysis-jvr2w"], True, True, False, 0.5, 2, monitor)
    c.run()
