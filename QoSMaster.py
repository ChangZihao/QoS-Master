from flask import Flask, request
import logger
import logic
import globalInfo
app = Flask("flask.app")


@app.route('/')
def test_index():
    return '<h1>Hello World</h1>'


@app.route('/register')
def register_index():
    node = request.args.get("node")
    appName = request.args.get("app")
    pod = request.args.get("pod")
    app.logger.info("Recive register: <%s, %s, %s>", node, appName, pod)
    if node is not None and appName is not None and pod is not None:
        res = logic.register(node, appName, pod)
        if res is True:
            return 'register success!'
        else:
            return 'register failed!'
    else:
        app.logger.error("Register failed by None value!")
        return 'register failed!'


@app.route('/stop')
def stop_index():
    pod = request.args.get("pod")
    app.logger.info("Recive stop: <%s>", pod)
    globalInfo.DeletRegister(pod)
    return 'register success!'


@app.route('/loadConfig')
def loadConfig_index():
    app.logger.info("Recive load config.")
    logic.loadConfig()
    print(globalInfo.GetRules())
    return 'Load config success!'


if __name__ == '__main__':
    logger.create_logger("flask.app")
    app.run(host='0.0.0.0', port=9002)
