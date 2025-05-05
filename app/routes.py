from flask import Blueprint, render_template

from app.main_process import home_logic, controladores_pid

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    # Obter a imagem em base64 gerada pela lógica
    image_base64, k, tau, theta = home_logic()

    return render_template("home.html", image_base64=image_base64, k=k, tau=tau, theta=theta)


@bp.route("/controladores_pid")
def controladores_pid():
    # Obter a imagem em base64 gerada pela lógica
    image_base64 = controladores_pid()

    return render_template("home.html", image_base64=image_base64)
