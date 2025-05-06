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
    y_sim_fopdt = y_sim_fopdt * step

    # Simular a resposta ao degrau do sistema identificado
    t_sim_ident, y_sim_ident = step_response(f_identification, T=time_dataset)
    y_sim_ident = y_sim_ident * step

    # Criar o gráfico
    plt.figure(figsize=(6, 4))
    plt.plot(time_dataset, y_sim_fopdt, "b", label="Referencia")
    plt.plot(time_dataset, y_sim_ident, "m--", label=f"Modelo ({best_method})")

    plt.title(f"Gráfico do Método: {best_method}")
    plt.legend()
    plt.xlabel("Tempo (s)")
    plt.ylabel("Temperatura (C°)")
    plt.ylim(
        [
            np.min([y_sim_fopdt, y_sim_ident]) - 1,
            np.max([y_sim_fopdt, y_sim_ident]) + 10,
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

    f_identification = tf([k_sun], [tau_sun, 1])
    num_delay, den_delay = pade(theta_sun, 2)

    delay = tf(num_delay, den_delay)
    f_identification = series(delay, f_identification)

    # Simular a resposta ao degrau do modelo FOPDT (modelo exato)
    t_sim_fopdt, y_sim_fopdt = step_response(fopdt_model_with_delay, T=time_dataset)
    y_sim_fopdt = y_sim_fopdt * step

    # Simular a resposta ao degrau do sistema identificado
    t_sim_ident, y_sim_ident = step_response(f_identification, T=time_dataset)
    y_sim_ident = y_sim_ident * step

    # Criar o gráfico
    plt.figure(figsize=(6, 4))
    plt.plot(time_dataset, y_sim_fopdt, "b", label="Referencia")
    plt.plot(time_dataset, y_sim_ident, "m--", label=f"Modelo Sundaresan")

    plt.title(f"K: {k_sun:.2f}, Tau: {tau_sun:.2f}, Theta: {theta_sun:.2f}, Eqm: {eqms['Sundaresan']:.2f}")
    plt.legend()
    plt.xlabel("Tempo (s)")
    plt.ylabel("Temperatura (C°)")
    plt.ylim(
        [
            np.min([y_sim_fopdt, y_sim_ident]) - 1,
            np.max([y_sim_fopdt, y_sim_ident]) + 10,
        ]
    )
    plt.grid(True)
    # Salvar o gráfico na área de trabalho
    plt.savefig(os.path.join(DESKTOP_FOLDER, f"Sundaresan.png"))

    # Salvar o gráfico em um buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.close()

    return image_base64, k, tau, theta, round(eqms[best_method], 3), time_dataset[-1]


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

    num_delay, den_delay = pade(theta, 6)
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
