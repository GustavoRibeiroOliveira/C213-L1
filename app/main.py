import matplotlib.pyplot as plt
import numpy as np
from control import tf, pade, series
import io
import base64
from control import step_response

from app.identificationProcess import carregar_dataset, identification_process, identificar_fopdt


def home_logic():
    from scipy.interpolate import interp1d

    # Carregar o dataset da mesma pasta
    time_dataset, step, output_dataset = carregar_dataset()

    # Calcular os parâmetros para os diferentes métodos de identificação
    K_sun, tau_sun, theta_sun, eqm_sun = identification_process(step, time_dataset, output_dataset, 'Sundaresan')
    K_smi, tau_smi, theta_smi, eqm_smi = identification_process(step, time_dataset, output_dataset, 'Smith')

    # Obter o modelo FOPDT com atraso via Padé (modelo exato)
    fopdt_model_with_delay = identificar_fopdt(step, time_dataset, output_dataset)

    # Comparar qual método gerou o menor EQM
    eqms = {'Sundaresan': eqm_sun, 'Smith': eqm_smi}
    best_method = min(eqms, key=eqms.get)

    # Definir o sistema conforme o melhor método
    if best_method == 'Sundaresan':
        f_identification = tf([K_sun], [tau_sun, 1])
        num_delay, den_delay = pade(theta_sun, 2)
    else:  # Smith
        f_identification = tf([K_smi], [tau_smi, 1])
        num_delay, den_delay = pade(theta_smi, 2)

    delay = tf(num_delay, den_delay)
    f_identification = series(delay, f_identification)

    # Simular a resposta ao degrau do modelo FOPDT (modelo exato)
    t_sim_fopdt, y_sim_fopdt = step_response(fopdt_model_with_delay, T=time_dataset)

    # Simular a resposta ao degrau do sistema identificado
    t_sim_ident, y_sim_ident = step_response(f_identification, T=time_dataset)

    # Interpolar para alinhar os tempos simulados com os reais
    interp_fopdt = interp1d(t_sim_fopdt, y_sim_fopdt, kind='linear', fill_value='extrapolate')
    y_sim_fopdt_interp = interp_fopdt(time_dataset)

    interp_ident = interp1d(t_sim_ident, y_sim_ident, kind='linear', fill_value='extrapolate')
    y_sim_ident_interp = interp_ident(time_dataset)

    # Ajustar nível inicial do output real
    output_ref = output_dataset - output_dataset[0]

    # Criar o gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(time_dataset, y_sim_fopdt_interp, 'b--', label='Referencia')
    plt.plot(time_dataset, y_sim_ident_interp, 'm--', label=f'Modelo ({best_method})')

    plt.title(f'Gráfico - Melhor Método: {best_method}')
    plt.legend()
    plt.xlabel('Tempo')
    plt.ylabel('Temperatura')
    plt.ylim([np.min([y_sim_fopdt_interp, y_sim_ident_interp]) - 1,
              np.max([y_sim_fopdt_interp, y_sim_ident_interp]) + 1])
    plt.grid(True)

    # Salvar o gráfico em um buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return image_base64
