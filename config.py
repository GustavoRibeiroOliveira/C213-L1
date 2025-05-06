import os
import sys
from socket import socket

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def resource_path(relative_path):
    """Retorna o caminho absoluto para recurso, funciona com PyInstaller."""
    if getattr(sys, "frozen", False):
        # Executável criado com PyInstaller
        base_path = sys._MEIPASS
    else:
        # Rodando via interpretador normal (dev)
        base_path = os.path.abspath(".")
        base_path = os.path.join(base_path, "app")
    return os.path.join(base_path, relative_path)


DESKTOP_FOLDER = os.path.join(os.environ["USERPROFILE"], "Desktop")
STATIC_FOLDER = resource_path("static")
TEMPLATE_FOLDER = resource_path("templates")


def find_available_port():
    with socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


HOST = "127.0.0.1"
PORT = find_available_port()


class Config:
    FLASK_DEBUG = 1
    SESSION_TYPE = "filesystem"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///banco.db"


class Config:
    FLASK_DEBUG = 1
    SECRET_KEY = (
        "k\x8d-\xbd\xb9\x05\xeax\x92\xd9{H\xf0\x9c\xf9\xde\x91\xc6\xe6\xa8\x14\xf9\x89t"
    )
