import logging

from multiprocessing import Process

from flask import Flask

import config

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("Server")

app = Flask(__name__)

_proc_server = None
_proc_da = None


@app.route('/restart_server/', methods=['GET'])
def restart_server():
    global _proc_server
    if _proc_server:
        _proc_server.terminate()
        _proc_server.join()
        _proc_server = None

    _proc_server = Process(target=_start_server, daemon=True)
    _proc_server.start()
    return 'ok'


@app.route('/restart_da/', methods=['GET'])
def restart_da():
    global _proc_da
    if _proc_da:
        _proc_da.terminate()
        _proc_da.join()
        _proc_da = None

    _proc_da = Process(target=_start_da, daemon=True)
    _proc_da.start()
    return 'ok'


def _start_server():
    from app import main as server
    server()


def _start_da():
    if config.IOTTALK_VERSION == 1:
    	from da.DAI import main as da
    elif config.IOTTALK_VERSION == 2:
    	from da.sa import main as da
    da()


def main():
    app.run('localhost', port=config.RESTART_SERVER_PORT)


if __name__ == '__main__':
    restart_server()
    restart_da()
    main()
