import base64
import io
import os
import matplotlib
matplotlib.use("Agg")  # Usa backend sem GUI
import matplotlib.pyplot as plt
import numpy as np
from control import pade, series, step_response, tf
from scipy.interpolate import interp1d

from app.utils import (
    calcular_overshoot,
    carregar_dataset,
    chr_com_sobre_valor,
    identificar_fopdt,
    identification_process,
    ziegler_nichols_malha_aberta,
)
from config import DESKTOP_FOLDER



def home_logic():

    # Carregar o dataset da mesma pasta
    time_dataset, step, output_dataset = carregar_dataset()

    # Calcular os parâmetros para os diferentes métodos de identificação
    k_sun, tau_sun, theta_sun, eqm_sun = identification_process(
        step, time_dataset, output_dataset, "Sundaresan"
    )
    k_smi, tau_smi, theta_smi, eqm_smi = identification_process(
        step, time_dataset, output_dataset, "Smith"
    )

    # Obter o modelo FOPDT com atraso via Padé (modelo exato)
    fopdt_model_with_delay = identificar_fopdt(step, time_dataset, output_dataset)

    # Comparar qual método gerou o menor EQM
    eqms = {"Sundaresan": eqm_sun, "Smith": eqm_smi}
    best_method = min(eqms, key=eqms.get)

    # Definir o sistema conforme o melhor método
    if best_method == "Sundaresan":
        f_identification = tf([k_sun], [tau_sun, 1])
        num_delay, den_delay = pade(theta_sun, 2)
        k = round(k_sun, 3)
        tau = round(tau_sun, 3)
        theta = round(theta_sun, 3)
    else:  # Smith
        f_identification = tf([k_smi], [tau_smi, 1])
        num_delay, den_delay = pade(theta_smi, 2)
        k = round(k_smi, 3)
        tau = round(tau_smi, 3)
        theta = round(theta_smi, 3)

    delay = tf(num_delay, den_delay)
    f_identification = series(delay, f_identification)

    # Simular a resposta ao degrau do modelo FOPDT (modelo exato)
    t_sim_fopdt, y_sim_fopdt = step_response(fopdt_model_with_delay, T=time_dataset)

    # Simular a resposta ao degrau do sistema identificado
    t_sim_ident, y_sim_ident = step_response(f_identification, T=time_dataset)

    # Interpolar para alinhar os tempos simulados com os reais
    interp_fopdt = interp1d(
        t_sim_fopdt, y_sim_fopdt, kind="linear", fill_value="extrapolate"
    )
    y_sim_fopdt_interp = interp_fopdt(time_dataset)

    interp_ident = interp1d(
        t_sim_ident, y_sim_ident, kind="linear", fill_value="extrapolate"
    )
    y_sim_ident_interp = interp_ident(time_dataset)

    # Ajustar nível inicial do output real
    # output_ref = output_dataset - output_dataset[0]

    # Criar o gráfico
    plt.figure(figsize=(6, 4))
    plt.plot(time_dataset, y_sim_fopdt_interp, "b--", label="Referencia")
    plt.plot(time_dataset, y_sim_ident_interp, "m--", label=f"Modelo ({best_method})")

    plt.title(f"Gráfico do Método: {best_method}")
    plt.legend()
    plt.xlabel("Tempo (s)")
    plt.ylabel("Temperatura (C°)")
    plt.ylim(
        [
            np.min([y_sim_fopdt_interp, y_sim_ident_interp]) - 1,
            np.max([y_sim_fopdt_interp, y_sim_ident_interp]) + 1,
        ]
    )
    plt.grid(True)
    # Salvar o gráfico na área de trabalho
    plt.savefig(os.path.join(DESKTOP_FOLDER, f"{best_method}.png"))

    # Salvar o gráfico em um buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return image_base64, k, tau, theta


def controladores_pid(k, tau, theta, method, kp=None, ti=None, td=None):
    nomes_dos_metodos = {
        "zn": "Ziegler Nichols",
        "chr": "CHR (com sobrevalor)",
        "manual": "Sintonia Manual",
    }
    if method == "zn":
        kp, ti, td = ziegler_nichols_malha_aberta(k, tau, theta)
    elif method == "chr":
        kp, ti, td = chr_com_sobre_valor(k, tau, theta)

    overshoot, t, yout = calcular_overshoot(kp, ti, td, k, tau, theta)

    # Plotar o gráfico
    plt.figure(figsize=(6, 4))
    plt.plot(t, yout, label="Resposta ao Degrau (PID)")

    # Mostrar linha de overshoot
    y_max = np.max(yout)
    plt.axhline(
        y_max, color="red", linestyle="--", label=f"Overshoot: {overshoot:.2f}%"
    )

    plt.title(f"Resposta ao Degrau - Método {nomes_dos_metodos[method]}")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Saída")
    plt.grid(True)
    plt.legend()

    # Salvar na área de trabalho
    filename = f"resposta_pid_{nomes_dos_metodos[method]}.png"
    path = os.path.join(DESKTOP_FOLDER, filename)
    plt.savefig(path)

    # Salvar em base64 para retornar à interface
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close()

    return image_base64, kp, ti, td, overshoot
