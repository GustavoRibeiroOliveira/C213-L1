import os
import sys

import numpy as np
from control import pade, series, step_response, tf, feedback
from scipy.interpolate import interp1d
from scipy.io import loadmat


def identificar_fopdt(step, time_dataset, output_dataset):
    """
    Identifica um modelo de processo de primeira ordem com atraso (FOPDT - First Order Plus Dead Time)
    a partir dos dados fornecidos.

    Esta função utiliza os dados de entrada e saída do processo para calcular os parâmetros de um modelo
    FOPDT, que consiste em:
    - Ganho estático (K)
    - Tempo morto (θ)
    - Constante de tempo (τ)

    A função usa a abordagem clássica para estimar os parâmetros:
    1. O ganho estático (K) é calculado como a razão entre a variação final da saída e a variação do degrau aplicado.
    2. O tempo morto (θ) é estimado como o tempo até a primeira mudança na saída após o degrau.
    3. A constante de tempo (τ) é estimada com base na aproximação de 63,21% da variação total da saída.
    4. A função também gera o modelo FOPDT aproximado como uma função de transferência com o atraso modelado por uma aproximação de Padé.

    Args:
    - input_dataset (numpy.ndarray): Vetor contendo o sinal de entrada (geralmente o degrau aplicado).
    - time_dataset (numpy.ndarray): Vetor de tempos correspondentes aos dados de entrada e saída.
    - output_dataset (numpy.ndarray): Vetor contendo a saída do sistema, como a temperatura ou outra variável medida.

    Returns:
    - g_total (TransferFunction): Modelo de processo identificado como uma função de transferência (FOPDT) com atraso.
      O modelo é representado pela função de transferência G(s) = K / (τs + 1) com atraso θ aproximado pela
      aproximação de Padé.

    Exceções:
    - Levanta `ValueError` se os tamanhos dos vetores de entrada e saída não coincidirem.
    - Levanta `IndexError` se o processo não mostrar uma mudança detectável.

    Exemplo:
        input_data = np.array([...])  # Dados de entrada
        time_data = np.array([...])   # Dados de tempo
        output_data = np.array([...]) # Dados de saída

        modelo = identificar_fopdt(input_data, time_data, output_data)
        print(modelo)
    """
    # Cálculo do ganho estático K
    valor_inicial = output_dataset[0]

    # Padroniza a saída
    output_padronizado = output_dataset - valor_inicial
    K = output_padronizado[-1] / step

    # Estimativa do tempo morto (theta)
    idx_mudanca = np.where(output_dataset != output_dataset[0])[0][0] - 1
    theta = time_dataset[idx_mudanca]

    # Cálculo da constante de tempo (tau) - ponto de 63.21%
    valor_referencia = 0.6321 * output_padronizado[-1]
    index_valor_referencia = np.where(output_padronizado >= valor_referencia)[0][0]
    tau = time_dataset[index_valor_referencia] - theta

    # Parte sem atraso
    g = tf([K], [tau, 1])  # G(s) = K / (τs + 1)

    # Aproximação de Padé para o atraso
    num_delay, den_delay = pade(theta, 6)
    delay = tf(num_delay, den_delay)

    # Sistema com atraso aproximado
    g_total = series(delay, g)

    return g_total


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
    valor_inicial = output[0]
    output_padronizado = output - valor_inicial
    k = output_padronizado[-1] / step

    if method == "Smith":
        val1 = 0.283 * output_padronizado[-1]
        val2 = 0.632 * output_padronizado[-1]
    else:  # Sundaresan
        val1 = 0.353 * output_padronizado[-1]
        val2 = 0.853 * output_padronizado[-1]

    index1 = np.where(output_padronizado >= val1)[0][0]
    index2 = np.where(output_padronizado >= val2)[0][0]
    t1 = time[index1]
    t2 = time[index2]

    if method == "Smith":
        tau = (t2 - t1) * 1.5
        theta = t2 - tau
    else:  # Sundaresan
        tau = (t2 - t1) * (2 / 3)
        theta = (1.3 * t1) - (0.29 * t2)

    # Parte sem atraso
    G = tf([k], [tau, 1])

    # Aproximação de Padé para o atraso
    num_delay, den_delay = pade(theta, 6)
    delay = tf(num_delay, den_delay)

    # Sistema com atraso aproximado
    f_identification = series(delay, G)

    # Simular a resposta ao degrau do sistema identificado
    t_sim, y_sim = step_response(f_identification, T=time)
    y_sim = y_sim * step

    # Calcular EQM
    output_ref = output - output[0]
    eqm = np.sqrt(np.mean((output_ref - y_sim) ** 2))

    return k, tau, theta, eqm


def carregar_dataset():
    """
    Carrega um arquivo .MAT contendo dados de um experimento e retorna os datasets necessários.

    Esta função tenta carregar um arquivo MAT específico, localizando-o no mesmo diretório que o script.
    Os dados são extraídos a partir de chaves específicas do arquivo e divididos em três conjuntos:
    - Tempo do experimento.
    - Sinal de degrau aplicado.
    - Temperatura medida ao longo do tempo.

    A função verifica a existência do arquivo e, se encontrado, carrega os dados necessários em formato adequado.

    Caso o arquivo não seja encontrado, uma exceção `FileNotFoundError` será levantada.

    Retorna:
        - time_dataset (numpy.ndarray): Vetor com os tempos registrados durante o experimento.
        - step (numpy.ndarray): Vetor contendo os valores do degrau aplicado.
        - output_dataset (numpy.ndarray): Vetor com os valores de temperatura ao longo do tempo.

    Exceções:
        - Levanta um `FileNotFoundError` caso o arquivo MAT não seja encontrado no diretório.

    Exemplo:
        time, step, temperature = carregar_dataset()
    """
    # Detecta o diretório base, considerando execução com PyInstaller
    if getattr(sys, "frozen", False):
        # Executável gerado com PyInstaller
        base_path = sys._MEIPASS
        base_path = os.path.join(base_path, "app")
    else:
        # Execução normal (modo desenvolvimento)
        base_path = os.path.dirname(__file__)

    file_path = os.path.join(base_path, "Dataset_Grupo1.mat")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo {file_path} não encontrado.")

    data = loadmat(file_path)
    print("Chaves do arquivo .mat:", data.keys())

    # Obtem o objeto principal
    reaction_data = data["reactionExperiment"]

    # A estrutura está encapsulada — precisamos acessar o primeiro item [0][0]
    reaction_data = reaction_data[0, 0]

    # Separar os campos
    sample_time = reaction_data["sampleTime"].flatten()
    data_input = reaction_data["dataInput"].flatten()
    data_output = reaction_data["dataOutput"].flatten()
    physical_quantity = reaction_data["physicalQuantity"]
    units = reaction_data["units"]

    sample_time = sample_time.astype(np.float64)
    return sample_time, np.mean(data_input), data_output


def ziegler_nichols_malha_aberta(k, tau, theta):
    """
    Calcula os parâmetros PID usando o Método de Ziegler-Nichols para sintonia de controladores em malha aberta,
    baseado na resposta à curva de reação de um sistema.

    O método de Ziegler-Nichols para malha aberta é utilizado para sistemas que podem ser modelados como
    processos de primeira ordem com atraso (tempo morto). A sintonia é baseada na constante de tempo (τ),
    o tempo morto (θ) e o ganho do processo (k).

    Args:
    - k (float): Ganho do processo.
    - tau (float): Constante de tempo do processo.
    - theta (float): Tempo morto (dead time) do processo.

    Returns:
    - kp (float): Parâmetro (Kp) do controlador PID, ajustado para o método de Ziegler-Nichols.
    - ti (float): Parâmetro (Ti) do controlador PID (tempo integral).
    - td (float): Parâmetro (Td) do controlador PID (tempo derivativo).

    Exemplo:
    - Para um processo com (k = 1.5), (τ = 10) e (θ = 2), a função retornará os valores de (Kp), (Ti) e (Td) ajustados para malha aberta.
    """
    kp = 1.2 * (tau / (k * theta))
    ti = 2 * theta
    td = 0.5 * theta

    return kp, ti, td


def chr_com_sobre_valor(k, tau, theta, sobre_valor=1.2):
    """
    Calcula os parâmetros PID usando o Método Cohen-Hora (CHR) com aplicação de sobrevalor no ganho (Kp).

    O Método Cohen-Hora (CHR) é usado para sintonizar controladores PID em sistemas com tempo de resposta desejado.
    O sobrevalor aplicado ao ganho (K_p) permite uma resposta mais agressiva, ajustando a intensidade do controle.

    Args:
    - k (float): Ganho do processo.
    - tau (float): Constante de tempo do processo.
    - theta (float): Tempo morto (dead time) do processo.
    - sobre_valor (float, opcional): Fator de sobrevalor para o ganho (K_p). O valor padrão é 1.2.
      Um valor maior que 1 aumenta a intensidade do controle, tornando a resposta mais rápida.

    Returns:
    - kp (float): Parâmetro (K_p) do controlador PID.
    - ti (float): Parâmetro (T_i) do controlador PID (tempo integral).
    - td (float): Parâmetro (T_d) do controlador PID (tempo derivativo).

    Exemplo:
    - Para um processo com (k = 1.5), (tau = 10) e (theta = 2), e usando o sobrevalor padrão de 1.2,
      a função retornará os valores de (K_p), (T_i) e (T_d) ajustados.
    """
    kp = (0.95 * tau) / (k * theta)
    ti = 1.357 * tau
    td = 0.473 * theta

    kp *= sobre_valor

    return kp, ti, td


def calcular_overshoot(kp, ti, td, k, tau, theta, t_max):
    # Criar o controlador PID: Kp * (1 + 1/(Ti*s) + Td*s)
    s = tf("s")
    pid = kp * (1 + 1 / (ti * s) + td * s)

    # Planta (processo) com Padé para o atraso
    planta = k / (tau * s + 1)
    num_delay, den_delay = pade(theta, 2)
    atraso = tf(num_delay, den_delay)

    planta_com_atraso = series(atraso, planta)

    # Sistema em malha fechada com feedback unário
    sistema_malha_fechada = feedback(series(pid, planta_com_atraso), 1)

    # Simulação da resposta ao degrau
    tempo = np.arange(0, 31315, 5)
    tempo, yout = step_response(sistema_malha_fechada, T=tempo)

    # Cálculo do overshoot
    max_value = np.max(yout)
    final_value = yout[-1]
    if final_value != 0 and max_value > final_value:
        overshoot = (max_value - final_value) / final_value * 100
    else:
        overshoot = 0.0

    return overshoot, tempo, yout
