import os

import webview

from app import create_app
from config import HOST, PORT, socketio

app = create_app()


def run_socketio(app, host, port):
    socketio.run(app=app, host=host, port=port, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    window = webview.create_window(
        "VIVO RF CHECK",
        f"http://{HOST}:{PORT}",
        min_size=(1200, 700),
        maximized=False,
        text_select=True,
    )
    webview.start(run_socketio, (app, HOST, PORT), debug=True)

    os._exit(0)
