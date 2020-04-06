import os
import QoSPolicy.MAGI.estimator as es
import numpy as np
import math
import csv

TRAINCIRCLE = 20

RULEIPCBOUND = 1.8
mainExTar = ["ipc_metric", "llc_metric", "misses_metric"]
subTar = ["ipc_metric", "llc_metric", "misses_metric"]


class Policy:
    def __init__(self, group, groups, control_config, accuracy, monitor):
        self.own = group  # "app1"
        self.controlConfig = control_config
        self.estimator = es.Estimator(accuracy, group)
        self.groups = groups  # ["app1","app2"]
        self.currentInfo = {}
        self.roundHistoryX = []
        self.roundHistoryy = []
        self.monitor = monitor
    
        if os.access(es.SAVE_PATH + "history_" + self.own + ".csv", os.F_OK):
            con_F = open(es.SAVE_PATH + "history_" + self.own + ".csv", "r")
            csv_F = csv.reader(con_F)
            trans_list = []
            for row in csv_F:
                trans_list.append([float(x) for x in row])
            con_F.close()
            self.historyX = (np.array(trans_list)[:, 0:-1]).tolist()
            self.historyy = (np.array(trans_list)[:, -1]).tolist()

        else:
            print("no history data")
            self.historyX = []
            self.historyy = []
        self.count = 0

    def with_run(self, infoList, train_enable):
        print("Policy:with_run")
        self.currentInfo = infoList
        print(str(infoList))
        X, y = self.generate_one_train_data(infoList)
        self.roundHistoryX.append(X)
        self.roundHistoryy.append(y)
        self.count += 1
        print("    round history count: " + str(self.count))
        if self.count == TRAINCIRCLE:
            print("TRAIN")
            # print(self.roundHistoryX)
            # print(self.roundHistoryy)
            self.estimator.scaler_init(self.roundHistoryX)
            print(self.roundHistoryX)
            train_X, train_y = self.estimator.pre_data(
                self.roundHistoryX, self.roundHistoryy)
            print(self.roundHistoryX)
            self.historyX += train_X.tolist()
            self.historyy += train_y.tolist()
            self.roundHistoryX.clear()
            self.roundHistoryy.clear()  # can store to local disk for future use
            store_content = np.column_stack((train_X, train_y))
            # historyXF = open(es.SAVE_PATH  + "historyX_" + self.own + ".txt", 'a')
            # historyyF = open(es.SAVE_PATH  + "historyy_" + self.own + ".txt", 'a')
            historyF = open(es.SAVE_PATH + "history_" + self.own + ".csv", 'a')
            csv.writer(historyF).writerows(store_content)
            # csv.writer(historyyF).writerows(self.historyy)
            # json.dump({str(self.own):self.historyX},historyXF)
            # json.dump({str(self.own):self.historyy},historyyF)
            # historyXF.close()
            historyF.close()
            self.count = 0
            if train_enable:
                # print(str(np.array(self.historyX).shape) + str(np.array(self.historyy).shape))
                self.estimator.train(
                    np.array(self.historyX), np.array(self.historyy))
            # print(str(self.currentInfo))
            # print(str(train_X.tolist()))
            # print(str(train_y.tolist()))

    def generate_one_train_data(self, infoList):
        print("Policy:generate_one_train_data")
        train_X = []
        for tar in subTar:
            if tar != "cycles":
                # infoList["app1"][...]
                train_X.append(infoList[self.own][tar])
        for tar in mainExTar:
            train_X.append(infoList[self.own][tar])
        for g in self.groups:  # groups:["app1","app2"] g: "app1"
            if g != self.own:
                for tar in subTar:
                    train_X.append(infoList[g][tar])
        train_y = float(infoList[self.own]["ipc_metric"])
        return train_X, train_y

    def diff_index(self, x1, x2):
        # print("Policy:diff_index")
        dist = np.linalg.norm(np.array(x1) - np.array(x2))
        # print(str(x1))

        sepDiff = []
        main1 = []
        main2 = []
        mainNum = len(subTar)+len(mainExTar) - 1
        for i in range(mainNum):
            main1.append(x1[i])
            main2.append(x2[i])
        sepDiff.append(np.linalg.norm(np.array(main1) - np.array(main2)))
        for i in range(len(self.groups) - 1):
            sub1 = []
            sub2 = []
            for j in range(len(subTar)):
                sub1.append(x1[mainNum + j])
                sub2.append(x2[mainNum + j])
            sepDiff.append(np.linalg.norm(np.array(sub1) - np.array(sub2)))
            mainNum += len(subTar) - 1
            # print(str(sub1))
            # print(mainNum)
        diffSum = np.sum(np.array(sepDiff))
        std_entropy = 0.0
        for d in sepDiff:
            if float(diffSum) == 0:
                return -1
            p = float(d)/float(diffSum)
            # print("p = " + str(p))
            if p == 0:
                continue
            if p < 0:
                return -1
            std_entropy -= math.log(p, 2) * p
        return dist * (1.0 + std_entropy)

    def find_basic_x(self, curr_x, sla):
        print("Policy:find_basic_x")
        small_set = self.estimator.find_sv_statisfy_v(
            self.historyX, self.historyy, sla)
        if small_set == -1:
            return -1
        basic_x = None
        least_diff = 999999999999999999.9
        for x in small_set:
            tmp_diff = self.diff_index(curr_x, x)
            if tmp_diff == -1:
                # print("small set len now is:" + str(len(small_set)))
                continue
            if tmp_diff < least_diff:
                least_diff = tmp_diff
                basic_x = x
        return basic_x

    def select_throttle_target(self, sla):
        print("Policy:select_throttle_target")
        # print(len(self.roundHistoryX))
        if len(self.historyX) == 0:
            return None
        # why not use currentInfo? because the main app don't have cycles
        curr_x = self.historyX[-1]
        basic_x = self.find_basic_x(curr_x, sla)
        if basic_x == -1 or basic_x is None:
            return None
        # print(str(np.array(basic_x).shape))
        base_ipc = self.estimator.inference(basic_x)
        # print("curr_x:" + str(curr_x) + "    basic_x:" + str(basic_x))
        # print("base_ipc:" + str(base_ipc))
        # print("base_x:" + str(basic_x))
        i = 0
        biggest_delta = 0
        target = ""
        for g in self.groups:
            if g != self.own:
                new_x = basic_x
                # -1 for except cycles in main app
                g_start = len(mainExTar) + len(subTar) + i * len(subTar) - 1
                i += 1
                for j in range(len(subTar)):
                    new_x[g_start + j] = curr_x[g_start + j]
                # print("new_x:" + str(new_x))
                guess = self.estimator.inference(new_x)
                if abs(float(guess) - base_ipc) >= biggest_delta:
                    biggest_delta = abs(float(guess) - base_ipc)
                    target = g
        return target

    def set_throttle_setup(self, badGroup, throttled_group):
        print("Policy:set_throttle_setup")
        if badGroup is None or badGroup == "":
            print("Warining: Single process? Just Ignore.Or badGroup is None")
            return 0
        curGI = self.currentInfo[self.own]
        if curGI['cpu_share'] > 25:
            for pod in self.monitor.getPodNameByapp(badGroup):
                self.monitor.action(pod, "cpu_share", curGI["cpu_share"] - 25)
        if curGI['llc_capacity'] > 0:
            for pod in self.monitor.getPodNameByapp(badGroup):
                self.monitor.action(pod, "llc", curGI["llc_capacity"] - 1)
        throttled_group.add(badGroup)
        return 0

    def throttle_target_select_setup(self, throttled_group, sla):
        print("Policy:throttle_target_select_setup")
        badGroup = self.select_throttle_target(sla)
        if badGroup is None or badGroup == "":
            # self.logger.info("Group %s policy %s returns None,fall back",group,policy.name)
            print("Have no targets")
            return -1
        else:
            # self.logger.info("using policy %s to make decision",policy.name)
            if self.set_throttle_setup(badGroup, throttled_group) == -1:
                print("Warning: set_throttle_setup fail")
            return 0

    # RULE Model

    def rule_update(self, throttled_group):
        print("Policy:rule_update")
        print("App: %s", self.own)
        curGI = self.currentInfo[self.own]
        print("curGI: %s", curGI)
        print("pod: %s", self.monitor.pods)
        if curGI["ipc_metric"] < self.controlConfig[self.own]["SLA"]["ipc"] and curGI["misses_metric"] > 70:
            if curGI["llc_capacity"] < self.controlConfig[self.own]["maximum_setups"]["llc"]:
                for pod in self.monitor.getPodNameByapp(self.own):
                    self.monitor.action(pod, "llc", curGI["llc_capacity"] + 1)
                return 0
            if curGI['cpu_share'] < self.controlConfig[self.own]["maximum_setups"]["cpu_share"]:
                for pod in self.monitor.getPodNameByapp(self.own):
                    self.monitor.action(pod, "cpu_share", curGI["cpu_share"] + 25)
                return 0

            relax_apps = {}
            for app, metrics in self.currentInfo.items():
                if app != self.own and metrics["ipc_metric"] > self.controlConfig[self.own]["SLA"]["ipc"]:
                    relax = metrics["ipc_metric"] * (metrics["cpu_share"] - self.controlConfig[self.own]["minimum_setups"]["cpu_share"]) * (metrics["llc_capacity"] - self.controlConfig[self.own]["minimum_setups"]["llc"])
                    relax_apps[app] = relax
            if len(relax_apps) > 0:
                relax_max = sorted(relax_apps.items(), key=lambda x: x[1], reverse=True)[0]
                if curGI['cpu_share'] > 25:
                    for pod in self.monitor.getPodNameByapp(relax_max[0]):
                        self.monitor.action(pod, "cpu_share", curGI["cpu_share"] - 25)
                    throttled_group.add(relax_max[0])
                if curGI['llc_capacity'] > 0:
                    for pod in self.monitor.getPodNameByapp(relax_max[0]):
                        self.monitor.action(pod, "llc", curGI["llc_capacity"] - 1)
                    throttled_group.add(relax_max[0])
                return 0

            else:
                print("do not find relax app!")
                return -1
