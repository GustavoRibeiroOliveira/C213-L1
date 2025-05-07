from flask import Blueprint, render_template, request, jsonify

from app.main_process import controladores_pid, home_logic

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    # Obter as imagens geradas pela lógica (malha aberta e malha fechada)
    image_open_base64, image_closed_base64, k, tau, theta, eqm, last_time = home_logic()

    return render_template(
        "home.html",
        image_open_base64=image_open_base64,
        image_closed_base64=image_closed_base64,
        k=k,
        tau=tau,
        theta=theta,
        eqm=eqm,
        last_time=last_time
    )


@bp.route("/gerar_pid", methods=["POST"])
def gerar_pid():
    data = request.json
    k = float(data["k"])
    tau = float(data["tau"])
    theta = float(data["theta"])
    method = data["method"]
    last_time = float(data["last_time"])
    if method == "manual":
        kp = float(data["kp"])
        ti = float(data["ti"])
        td = float(data["td"])
    else:
        kp = None
        ti = None
        td = None

    img_base64, kp, ti, td, overshoot = controladores_pid(
        k, tau, theta, method, kp, ti, td,
    )
    return jsonify(
        {"image": img_base64, "kp": kp, "ti": ti, "td": td, "overshoot": overshoot}
    )
