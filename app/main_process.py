import base64
import io
import os
import matplotlib
from control import feedback

matplotlib.use("Agg")  # Usa backend sem GUI
import matplotlib.pyplot as plt
import numpy as np
from control import pade, series, step_response, tf

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
    time_dataset, step, output_dataset = carregar_dataset()

    # Calcular os parâmetros para os diferentes métodos
    k_sun, tau_sun, theta_sun, eqm_sun = identification_process(step, time_dataset, output_dataset, "Sundaresan")
    k_smi, tau_smi, theta_smi, eqm_smi = identification_process(step, time_dataset, output_dataset, "Smith")

    # Modelo FOPDT real
    fopdt_model_with_delay = identificar_fopdt(step, time_dataset, output_dataset)
    t_sim_fopdt, y_sim_fopdt = step_response(fopdt_model_with_delay, T=time_dataset)
    y_sim_fopdt *= step

    # Seleção do melhor método
    eqms = {"Sundaresan": eqm_sun, "Smith": eqm_smi}
    best_method = min(eqms, key=eqms.get)
    other_method = "Smith" if best_method == "Sundaresan" else "Sundaresan"

    # Dicionários para acesso dinâmico
    params = {
        "Sundaresan": (k_sun, tau_sun, theta_sun),
        "Smith": (k_smi, tau_smi, theta_smi)
    }

    # -------- MELHOR MÉTODO --------
    k, tau, theta = params[best_method]
    f_identification = tf([k], [tau, 1])
    num_delay, den_delay = pade(theta, 6)
    f_identification = series(tf(num_delay, den_delay), f_identification)

    # Malha aberta
    t_open, y_open = step_response(f_identification, T=time_dataset)
    y_open *= step

    # Malha fechada
    system_closed = feedback(f_identification, 1)
    t_closed, y_closed = step_response(system_closed, T=time_dataset)
    y_closed *= step

    # Gráfico de malha aberta
    plt.figure(figsize=(6, 4))
    plt.plot(time_dataset, y_sim_fopdt, "b", label="Referência")
    plt.plot(t_open, y_open, "m--", label=best_method)
    plt.title(f"Malha Aberta - {best_method}")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Temperatura (C°)")
    plt.legend()
    plt.grid(True)
    buf_open = io.BytesIO()
    plt.savefig(buf_open, format="png")
    buf_open.seek(0)
    image_base64_open = base64.b64encode(buf_open.read()).decode("utf-8")
    buf_open.close()
    plt.savefig(os.path.join(DESKTOP_FOLDER, f"{best_method}_malha_aberta.png"))  # Salvar no desktop

    # Gráfico de malha fechada
    plt.figure(figsize=(6, 4))
    plt.plot(time_dataset, y_sim_fopdt, "b", label="Referência")
    plt.plot(t_closed, y_closed, "g--", label=best_method)
    plt.title(f"Malha Fechada - {best_method}")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Temperatura (C°)")
    plt.legend()
    plt.grid(True)
    buf_closed = io.BytesIO()
    plt.savefig(buf_closed, format="png")
    buf_closed.seek(0)
    image_base64_closed = base64.b64encode(buf_closed.read()).decode("utf-8")
    buf_closed.close()
    plt.savefig(os.path.join(DESKTOP_FOLDER, f"{best_method}_malha_fechada.png"))  # Salvar no desktop

    # -------- OUTRO MÉTODO (APENAS SALVAR) --------
    k_o, tau_o, theta_o = params[other_method]
    f_other = tf([k_o], [tau_o, 1])
    num_d_o, den_d_o = pade(theta_o, 2)
    f_other = series(tf(num_d_o, den_d_o), f_other)

    t_other_open, y_other_open = step_response(f_other, T=time_dataset)
    y_other_open *= step

    system_closed_other = feedback(f_other, 1)
    t_other_closed, y_other_closed = step_response(system_closed_other, T=time_dataset)
    y_other_closed *= step

    # Malha aberta - outro método
    plt.figure(figsize=(6, 4))
    plt.plot(time_dataset, y_sim_fopdt, "b", label="Referência")
    plt.plot(t_other_open, y_other_open, "m--", label=other_method)
    plt.title(f"Malha Aberta - {other_method}")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Temperatura (C°)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(DESKTOP_FOLDER, f"{other_method}_malha_aberta.png"))

    # Malha fechada - outro método
    plt.figure(figsize=(6, 4))
    plt.plot(time_dataset, y_sim_fopdt, "b", label="Referência")
    plt.plot(t_other_closed, y_other_closed, "g--", label=other_method)
    plt.title(f"Malha Fechada - {other_method}")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Temperatura (C°)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(DESKTOP_FOLDER, f"{other_method}_malha_fechada.png"))

    # -------- RETORNO --------
    return (
        image_base64_open,        # imagem do gráfico malha aberta
        image_base64_closed,      # imagem do gráfico da malha fechada
        round(k, 3),
        round(tau, 3),
        round(theta, 3),
        round(eqms[best_method], 3),
        time_dataset[-1]
    )




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

    # Criar função de transferência do controlador PID
    PID = tf([kp * td, kp, kp / ti], [1, 0])

    # Sistema de processo (sem controle)
    G = tf([k], [tau, 1])

    num_delay, den_delay = pade(theta, 2)
    delay = tf(num_delay, den_delay)

    # Sistema com atraso
    sistema = series(delay, G)

    # Sistema em malha fechada com PID
    malha_fechada = feedback(series(PID, sistema), 1)

    # Resposta ao degrau
    t, y = step_response(malha_fechada)
    y_max = np.max(y)
    y_min = np.min(y)

    # Plot
    plt.figure(figsize=(6, 4))
    plt.plot(t, y, label="PID", color="blue")
    plt.axhline(y_max, linestyle="--", color="red", label=f"Overshoot ~ {round((y_max - 1) * 100, 2)}%")
    plt.grid(True)
    plt.legend(loc="lower right")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Temperatura [°C]")
    plt.title(f"Sistema com Controle PID - {method}")

    # Garantir que o ylim cobre todo o sinal com 5% de margem
    margem = 0.05
    delta = (y_max - y_min) * margem
    plt.ylim([y_min - delta, y_max + delta])

    # Salvar imagem
    filename = f"PID_Metodo_{nomes_dos_metodos[method].replace(' ', '')}.png"
    path = os.path.join(DESKTOP_FOLDER, filename)
    plt.savefig(path)

    # Converter para base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close()

    # Overshoot calculado de forma simples aqui, pode substituir por uma função
    overshoot = round((y_max - 1) * 100, 2)

    return image_base64, kp, ti, td, overshoot
