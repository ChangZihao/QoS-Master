# QoS-Master
QoS-Master是QoS-Serverless的中心节点，主要负责策略的管理和运行。

# QoS-Master对外接口：

* \[ip]:9002/register：注册pod，匹配&启动策略。
* \[ip]:9002/loadConfig：更新加载QoS-Master策略。
* \[ip]:9002/stop：停止pod的策略管理。

QoS-Master接口在QoS-Master/QoSMaster.py中定义，具体实现在QoS-Master/logic中实现.py

# QoS策略
**QoS策略路径：**

QoS-Master/QoSPolicy/$PolicyName

**QoS策略启动接入流程：**

1. 启动函数：Run()是每个策略的启动函数，策略接入QoS-Master必须有Run()，函数格式如下
   
   def Run(rule, node, pod, monitor, flag)
   
   **参数含义**：
   
   * rule：QoS-Master的规则类，用于存储规则的，详情参见 QoS-Master/rule.py。
   * node：运行容器节点IP。
   * pod：容器的id，与容器cgroup的id对应。
   * monitor：QoS-Master为每个策略的监控对象，包含action、monitor和getPodNameByapp三个接口，详情参见QoS-Master/monitor.py。
   * flag：QoS-Master管理策略的运行状态的标志，有三种状态，运行、停止、完成。

2. 策略注册：将策略注册到QoS-Master系统中，详情参见QoS-Master/rule.py。
   
    ruleMap是策略的注册点，需要将策略的Run写入其中。
3. 配置管理：
   
   配置路径为：QoS-Master/config.json，为应用配置相关策略。

# Log机制：

QoS-Master封装有Logger功能，详情参见QoS-Master/logger.py，不同模块通过create_logger()可以创建log。
   




