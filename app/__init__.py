from flask import Flask

from app.routes import bp
from config import STATIC_FOLDER, TEMPLATE_FOLDER, ProductionConfig


def create_app(config_class=ProductionConfig):
    app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
    app.config.from_object(config_class)

    app.register_blueprint(bp)

    return app
