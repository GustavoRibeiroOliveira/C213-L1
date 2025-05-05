import numpy as np
from scipy.io import loadmat
import os
import sys
from control import tf, pade, series
from control import step_response
from scipy.interpolate import interp1d


def identificar_fopdt(input_dataset, time_dataset, output_dataset):
    # Cálculo do ganho estático K
    amplitude_degrau = np.mean(input_dataset)
    valor_inicial = output_dataset[0]

    # Padroniza a saída
    output_padronizado = output_dataset - valor_inicial
    K = output_padronizado[-1] / amplitude_degrau

    # Estimativa do tempo morto (theta)
    idx_mudanca = np.where(output_dataset != output_dataset[0])[0][0] - 1
    theta = time_dataset[idx_mudanca]

    # Cálculo da constante de tempo (tau) - ponto de 63.21%
    valor_referencia = 0.6321 * output_padronizado[-1]
    index_valor_referencia = np.where(output_padronizado >= valor_referencia)[0][0]
    tau = time_dataset[index_valor_referencia] - theta

    # Parte sem atraso
    G = tf([K], [tau, 1])  # G(s) = K / (tau*s + 1)

    # Aproximação de Padé para o atraso
    num_delay, den_delay = pade(theta, 2)  # Ordem 1 (pode usar 2 para mais precisão)
    delay = tf(num_delay, den_delay)

    # Sistema com atraso aproximado
    G_total = series(delay, G)

    return G_total


def identification_process(step, time, output, method):
    """
    identificationProcess identifies control systems using the Smith or Sundaresan methods based on
    test data, considering a First Order Plus Dead Time model.

    identification = identificationProcess(Step, Time, Output) performs system identification based
    on the step response with amplitude Step and the output samples Output over the sampling times
    Time.

    identification = identificationProcess(Step, Time, Output, 'Method', method) specifies the
    system identification method, valid as 'Smith' or 'Sundaresan'. The default method is Smith.

    Inputs:
      - Step   (scalar) Amplitude of the input step. Must be a finite, non-zero number.
      - Time   (array)  Sampling time points of the process. Must be non-empty.
      - Output (array)  Output samples of the process at the given sampling times. Must be non-empty.

    Output:
      - identification (dict) Dictionary containing the identified system parameters.
    """
    # Calcular o ganho estático K
    amplitude_degrau = np.mean(step)
    valor_inicial = output[0]
    output_padronizado = output - valor_inicial
    k = output_padronizado[-1] / amplitude_degrau

    if method == 'Smith':
        # Calcular a constante de tempo (tau)
        val1 = 0.283 * output_padronizado[-1]
        indice1 = np.where(output_padronizado >= val1)[0][0]
        t1 = time[indice1]
        val2 = 0.632 * output_padronizado[-1]
        indice2 = np.where(output_padronizado >= val2)[0][0]
        t2 = time[indice2]
        tau = (t2 - t1) * 1.5

        # Estimativa do atraso de tempo (theta)
        theta = t2 - tau
    else:
        # Calcular a constante de tempo (tau)
        val1 = 0.353 * output_padronizado[-1]
        indice1 = np.where(output_padronizado >= val1)[0][0]
        t1 = time[indice1]
        val2 = 0.853 * output_padronizado[-1]
        indice2 = np.where(output_padronizado >= val2)[0][0]
        t2 = time[indice2]
        tau = (t2 - t1) * (2 / 3)

        # Estimativa do atraso de tempo (theta)
        theta = (1.3 * t1) - (0.29 * t2)

    # Parte sem atraso
    G = tf([k], [tau, 1])  # G(s) = K / (tau*s + 1)

    # Aproximação de Padé para o atraso
    num_delay, den_delay = pade(theta, 2)  # Ordem 1 (pode usar 2 para mais precisão)
    delay = tf(num_delay, den_delay)

    # Sistema com atraso aproximado
    f_identification = series(delay, G)
    f_ref = identificar_fopdt(step, time, output)

    # Simular a resposta ao degrau do sistema identificado
    t_sim, y_sim = step_response(f_identification, T=time)

    # Interpolação para alinhar os tempos simulados com os tempos reais
    interp_sim = interp1d(t_sim, y_sim, kind='linear', fill_value='extrapolate')
    y_sim_interp = interp_sim(time)

    # Ajustar nível inicial do output real
    output_ref = output - output[0]

    # Calcular EQM
    eqm = np.mean((output_ref - y_sim_interp) ** 2)

    return k, tau, theta, eqm


def carregar_dataset():
    """
    Função para carregar o arquivo MAT e retornar os datasets necessários.
    """
    # # Interface gráfica para seleção de arquivos
    # root = Tk()
    # root.withdraw()  # Não exibe a janela principal
    # file_path = filedialog.askopenfilename(title="Selecione o arquivo .mat", filetypes=[("MAT Files", "*.mat")])
    #
    # if file_path:
    #     # Carregar o arquivo MAT
    #     data = loadmat(file_path)
    #
    #     # Verificar as chaves do arquivo para entender sua estrutura
    #     print("Chaves do arquivo .mat:", data.keys())  # Isso mostra as variáveis disponíveis
    #
    #     step = data['TARGET_DATA____Degrau']
    #     output_dataset = data['TARGET_DATA____Temperatura']
    #     time_dataset = output_dataset[:, 0]  # Tempo seria a primeira coluna
    #     return time_dataset, step, output_dataset
    file_path = os.path.join(os.path.dirname(__file__), 'EnsaioTemperatura_MA.mat')

    if os.path.exists(file_path):
        data = loadmat(file_path)

        # Verificar as chaves do arquivo para entender sua estrutura
        print("Chaves do arquivo .mat:", data.keys())

        step = data['TARGET_DATA____Degrau']
        output_dataset = data['TARGET_DATA____Temperatura']
        time_dataset = step[:, 0]  # tempo vem da primeira coluna
        step = step[:, 1]  # valor do degrau
        output_dataset = output_dataset[:, 1]  # valor da temperatura
        return time_dataset, step, output_dataset
    else:
        raise FileNotFoundError(f"Arquivo {file_path} não encontrado.")
