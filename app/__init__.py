from flask import Flask
from flask_socketio import SocketIO

from app.routes import bp
from config import STATIC_FOLDER, TEMPLATE_FOLDER, Config

socketio = SocketIO()


def create_app(config_class=Config, testing=False):
    app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
    app.config.from_object(config_class)

    if testing:
        app.config["TESTING"] = True
        app.config["DEBUG"] = False

    # Initialize SocketIO
    socketio.init_app(app, async_mode="threading")

    app.register_blueprint(bp)

    return app
