from flask import Blueprint, render_template

from app.main import home_logic

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    # Obter a imagem em base64 gerada pela lógica
    image_base64 = home_logic()

    return render_template("home.html", image_base64=image_base64)
