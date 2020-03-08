# cheated off of https://testdriven.io/blog/developing-a-single-page-app-with-flask-and-vuejs/
# cheated off of https://stackoverflow.com/questions/39801718

import os
import time
import json
from threading import Thread, Event
from typing import Dict, List, Any
import webbrowser

from flask import Flask, jsonify, request, send_from_directory, Response
import waitress

from isimple.util import suppress_stdout, Singleton
from isimple.core import get_logger, cache
from isimple.core.schema import schema
from isimple.video import Analyzer, AnalyzerType, backend
from isimple.history import History, AnalysisModel

log = get_logger('isimple')


UI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'dist')


def respond(*args) -> str:
    return jsonify(*args)


class ServerThread(Thread, metaclass=Singleton):
    _app: Flask
    _host: str
    _port: int

    def __init__(self, app, host, port):
        self._app = app
        self._host = host
        self._port = port
        super().__init__(daemon=True)

    def run(self):
        waitress.serve(
            self._app,
            host=self._host,
            port=self._port,
        )


class Main(object, metaclass=Singleton):
    _app: Flask

    _roots: Dict[str, Analyzer] = {}
    _models: Dict[str, AnalysisModel] = {}
    _history = History()

    _host: str = 'localhost'
    _port: int = 7951

    _server: Thread

    _ping = Event()
    _unload = Event()
    _quit = Event()

    _timeout_suppress = 0.5
    _timeout_unload = 1
    _timeout_loop = 0.1

    def __init__(self):
        app = Flask(__name__, static_url_path='')
        app.config.from_object(__name__)

        # Serve webapp
        @app.route('/', methods=['GET'])
        def open_gui():
            return send_from_directory(UI, 'index.html')

        @app.route('/<directory>/<file>', methods=['GET'])
        def get_file(directory, file):
            return send_from_directory(os.path.join(UI, directory), file)

        @app.route('/<file>', methods=['GET'])
        def get_file2(file):
            return send_from_directory(UI, file)

        # API: general
        @app.route('/api/ping')
        def ping():
            self._unload.clear()
            self._ping.set()
            return respond(True)

        @app.route('/api/unload', methods=['GET', 'POST'])
        def unload():
            self._unload.set()
            return respond(True)

        # API: working with Analyzer instances
        @app.route('/api/init/<id>', methods=['GET'])
        def init(id: str):  # todo: also add a model instance to self._models
            if 'type' in request.args.to_dict():
                bt = request.args.to_dict()['type']
            else:
                bt = None

            return respond(self.add_instance(id, AnalyzerType(bt)))

        @app.route('/api/list', methods=['GET'])
        def list():
            return respond([k for k in self._roots.keys()])

        @app.route('/api/<id>/schemas', methods=['GET'])
        def get_schemas(id: str):
            return respond(self.get_schemas(str(id)))

        @app.route('/api/<id>/launch', methods=['GET'])
        def launch(id: str):
            respond(self.call(str(id), 'launch', {}))

        @app.route('/api/<id>/can_launch', methods=['GET'])
        def can_launch(id: str):
            return respond(self.call(str(id), 'can_launch', {}))

        @app.route('/api/<id>/call/<endpoint>', methods=['GET'])
        def call(id: str, endpoint: str):
            return respond(self.call(str(id), endpoint, request.args.to_dict()))

        self._app = app

    def serve(self):
        # Don't show waitress console output (server URL)
        with suppress_stdout():
            ServerThread(self._app, self._host, self._port).start()

            # Run in separate thread to revent Ctrl+C from closing browser
            #  if no tabs were open before  todo: doesn't seem to work anymore?
            Thread(
                target=lambda: webbrowser.open(
                    f"http://{self._host}:{self._port}/"
                )
            ).start()

            time.sleep(self._timeout_suppress)  # Wait for Waitress to catch up

        while not self._quit.is_set():
            if self._ping.is_set():
                self._ping.clear()
            if self._unload.is_set():
                log.debug(f'Unloaded from browser, waiting for ping.')
                time.sleep(self._timeout_unload)
                if not self._ping.is_set():
                    log.debug('No ping received; quitting.')
                    self._quit.set()
                else:
                    log.debug('Ping received; cancelling.')
            time.sleep(self._timeout_loop)

    def add_instance(self, id: str, type: AnalyzerType = None) -> bool:
        if type is None:
            type = AnalyzerType()
        log.debug(f"Adding instance '{id}' (type: {type})")
        analyzer = type.get()()
        self._roots[str(id)] = analyzer
        self._models[str(id)] = self._history.add_analysis(analyzer)
        return True

    def get_schemas(self, id: str) -> dict:
        log.debug(f"Providing schemas for '{id}'")
        root = self._roots[id]
        return {
                'config': schema(root._config.__class__),
                'methods': {e.name:[schema(m) for m in ms] for e,ms in root.instance_mapping.items()}
        }

    def call(self, id: str, endpoint: str, data: dict) -> Any:
        log.debug(f"{self._roots[id]}: call '{endpoint}'")
        # todo: sanity check this
        method = self._roots[id].get(getattr(backend, endpoint))
        assert hasattr(method, '__call__')

        if endpoint in ('set_config',):
            pass  # todo: store to self._history

        return method(**{k:json.loads(v) for k,v in data.items()})


if __name__ == '__main__':
    # todo: take CLI arguments for address, debug on/off, ...
    # todo: server-level configuration?

    Main().serve()

