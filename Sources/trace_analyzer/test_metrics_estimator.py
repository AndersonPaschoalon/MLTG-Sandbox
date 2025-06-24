import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pywt
import scipy
from fbm import FBM
from scipy.stats import linregress
from sqlalchemy import TEXT, Column, ForeignKey, Integer, create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from commons.connectors.alchemy_connector import AlchemyConnector
from commons.models.packet import Packet


def _generate_synthetic_interarrival_df(
    n_packets=10000, process_type="self_similar", hurst=0.7, seed=42
):
    """
    Gera um DataFrame sintético de inter-chegadas de pacotes com diferentes tipos de processos.

    Parâmetros:
    -----------
    n_packets : int, opcional
        Número de pacotes a gerar. Padrão é 10000.
    process_type : str, opcional
        Tipo de processo a gerar:
        - 'exponential': Para tráfego com cauda leve (tipo Poisson).
        - 'pareto': Para tráfego com cauda pesada (pode exibir dependência de longo alcance).
        - 'self_similar': Gera tráfego com um expoente de Hurst predefinido usando fGn.
        Padrão é 'self_similar'.
    hurst : float, opcional
        O expoente de Hurst desejado se `process_type` for 'self_similar'.
        Deve estar entre 0.0 e 1.0. Padrão é 0.7.
    seed : int, opcional
        Semente aleatória para reprodutibilidade. Padrão é 42.

    Retorna:
    --------
    pd.DataFrame
        DataFrame com as colunas 'timestamp', 'inter_arrival', 'pkt_size', 'ttl'.
    """
    rng = np.random.default_rng(seed)
    inter_arrivals = np.array([])

    if process_type == "exponential":
        # Distribuição exponencial para tráfego com cauda leve (e.g., processos de Poisson)
        scale = 0.01  # Tempo médio entre chegadas
        inter_arrivals = rng.exponential(scale=scale, size=n_packets)
    elif process_type == "pareto":
        # Distribuição de Pareto para tráfego com cauda pesada.
        # 'a' é o parâmetro de forma. Valores menores de 'a' significam caudas mais pesadas.
        a_param = 1.5  # Um valor comum para tráfego de rede para LRD
        inter_arrivals = (
            rng.pareto(a=a_param, size=n_packets) * 0.01
        )  # Escala para tempos típicos
    elif process_type == "self_similar":
        # Gerar Ruído Gaussiano Fracionário (fGn) com o Hurst desejado usando a biblioteca fbm.
        # fGn são os incrementos de um Movimento Browniano Fracionário (fBm)
        # H deve estar entre 0 e 1.
        if not (0.0 < hurst < 1.0):  # H entre 0 e 1 (exclusivo para fGn)
            raise ValueError(
                "O expoente de Hurst para fGn deve estar estritamente entre 0.0 e 1.0."
            )

        # Instanciar um objeto FBM
        # n_samples = n_packets - 1 pois fGn retorna n-1 incrementos
        # para uma série de n pontos (ou n-1 inter-chegadas para n pacotes).
        # Ajustei para n_packets para garantir que teremos inter_arrivals suficientes.
        fbm_instance = FBM(n=n_packets, hurst=hurst)
        raw_fgn = (
            fbm_instance.fgn()
        )  # Chama o método fgn() para obter o Ruído Gaussiano Fracionário

        # Ajustar para que as inter-chegadas sejam positivas e tenham uma média razoável.
        # Os valores de fGn podem ser negativos e ter média 0.
        # Precisamos transladar e reescalar.

        # Vamos normalizar para uma média e desvio padrão esperados para inter-chegadas
        # Média e desvio padrão para inter-chegadas típicas de tráfego de rede
        target_mean = 0.01
        target_std = 0.005

        # Primeiro, reescalar o fGn para ter a média 0 e desvio padrão target_std
        # Evitar divisão por zero se o desvio padrão de raw_fgn for 0 (improvável, mas seguro)
        if np.std(raw_fgn) == 0:
            scaled_fgn = np.zeros_like(raw_fgn)
        else:
            scaled_fgn = (raw_fgn / np.std(raw_fgn)) * target_std

        # Em seguida, transladar para ter a média target_mean
        inter_arrivals = scaled_fgn + target_mean

        # Garante que todas as inter-chegadas sejam estritamente positivas.
        # Valores muito próximos de zero ou negativos podem causar problemas no cumsum ou em análises.
        inter_arrivals[inter_arrivals <= 0] = np.finfo(float).eps

        # Opcional: limitar valores muito grandes para evitar timestamps excessivamente longos
        # Isso pode "cortar" as caudas mais pesadas, mas garante estabilidade em simulações.
        inter_arrivals[inter_arrivals > 10] = 10

    else:
        raise ValueError(
            "Tipo de processo inválido. Escolha 'exponential', 'pareto' ou 'self_similar'."
        )

    # Calcula os timestamps acumulados a partir das inter-chegadas
    timestamps = np.cumsum(inter_arrivals)
    # Gera tamanhos de pacotes aleatórios dentro da faixa típica de Ethernet
    pkt_sizes = rng.integers(low=60, high=1514, size=n_packets)

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "inter_arrival": inter_arrivals,
            "pkt_size": pkt_sizes,
            "ttl": 64,  # TTL padrão para pacotes IP
        }
    )

    return df


def get_packet_arrival_df(connector: AlchemyConnector, flowID: int = 0) -> pd.DataFrame:
    """
    Creates a DataFrame with per-packet arrival information.

    Columns:
        - timestamp: Packet arrival time in seconds.
        - inter_arrival: Time difference between this packet and the previous one.
        - pkt_size: Size of the packet in bytes.
        - ttl: Time to Live field from the packet.

    Args:
        connector (AlchemyConnector): Active database connector.
        flowID (int): If > 0, filters packets by flow ID; otherwise includes all flows.

    Returns:
        pd.DataFrame: DataFrame with timestamp, inter-arrival time, packet size, and TTL.
    """
    with connector.session() as session:
        query = session.query(Packet).order_by(Packet.tsSec, Packet.tsUsec)
        if flowID > 0:
            packets = query.filter(Packet.flowID == flowID).all()
        else:
            packets = query.all()

        if not packets:
            return pd.DataFrame(
                columns=["timestamp", "inter_arrival", "pkt_size", "ttl"]
            )

        timestamps = [p.timestamp_seconds for p in packets]
        pkt_sizes = [p.pktSize for p in packets]
        ttls = [p.timeToLive for p in packets]

        # Calculate inter-arrival times (first is 0)
        inter_arrivals = [0] + [
            t2 - t1 for t1, t2 in zip(timestamps[:-1], timestamps[1:])
        ]

        df = pd.DataFrame(
            {
                "time": timestamps,
                "inter_arrival": inter_arrivals,
                "pkt_size": pkt_sizes,
                "ttl": ttls,
            }
        )

        return df


# --- Função Auxiliar Comum: Bining de Dados ---
# Será usada por ambas as funções de análise.
def _bin_packet_data(df, bin_width=0.01):
    """
    Agrega os dados de pacotes em bins de tempo fixos.

    Parâmetros:
    -----------
    df : pandas.DataFrame
        DataFrame de entrada com colunas 'timestamp' e 'pkt_size'.
    bin_width : float, opcional
        Largura de cada bin de tempo em segundos. Padrão é 0.01.

    Retorna:
    --------
    numpy.ndarray
        Array de bytes por bin de tempo.
    """
    time_start = df["timestamp"].min()
    time_end = df["timestamp"].max()
    bins = np.arange(time_start, time_end + bin_width, bin_width)
    df["time_bin"] = pd.cut(
        df["timestamp"], bins=bins, labels=False, include_lowest=True, right=False
    )
    bytes_per_bin = df.groupby("time_bin")["pkt_size"].sum().fillna(0).values
    return bytes_per_bin


def self_similarity_rs_cloudy(
    ac=None, flowID: int = 0, aggregation_levels: list[int] = [1, 5, 10, 50, 100, 500]
):
    def _rs_analysis_on_series_cloudy(series, block_sizes):
        log_ns, log_rss = [], []

        for n in block_sizes:
            if n >= len(series):
                continue

            step = max(1, n // 4)
            rs_values = []

            for start in range(0, len(series) - n + 1, step):
                block = series[start : start + n]
                mean = np.mean(block)
                dev = block - mean
                cum_dev = np.cumsum(dev)
                R = np.max(cum_dev) - np.min(cum_dev)
                S = np.std(block, ddof=1)
                if S != 0:
                    rs = R / S
                    log_ns.append(np.log2(n))
                    log_rss.append(np.log2(rs))

        rs_df = pd.DataFrame({"log_n": log_ns, "log_rs": log_rss})

        if not rs_df.empty:
            slope, _, _, _, _ = linregress(rs_df["log_n"], rs_df["log_rs"])
        else:
            slope = np.nan

        return rs_df, slope

    if ac is None:
        df = _generate_synthetic_interarrival_df()
    else:
        df = get_packet_arrival_df(ac, flowID=flowID)

    bin_width = 0.01
    time_start = df["timestamp"].min()
    time_end = df["timestamp"].max()
    bins = np.arange(time_start, time_end + bin_width, bin_width)
    df["time_bin"] = pd.cut(df["timestamp"], bins=bins, labels=False)
    bytes_per_bin = df.groupby("time_bin")["pkt_size"].sum().fillna(0).values

    # --- Cloudy R/S Plot (Figure 2a style) ---
    rs_df, _ = _rs_analysis_on_series_cloudy(
        bytes_per_bin, block_sizes=[2, 4, 8, 16, 32, 64, 128]
    )
    x = rs_df["log_n"]
    rs_df["slope_1_line"] = x * 1.0
    rs_df["slope_half_line"] = x * 0.5

    # --- Hurst vs Aggregation Level (Figure 2d style) ---
    hurst_vs_m = []
    rs_agr = []
    for m in aggregation_levels:
        n = len(bytes_per_bin) // m
        truncated = bytes_per_bin[: n * m]
        agg_series = truncated.reshape((n, m)).mean(axis=1)
        rs, hurst = _rs_analysis_on_series_cloudy(
            agg_series, block_sizes=[2, 4, 8, 16, 32]
        )
        hurst_vs_m.append((m, hurst))
        rs_agr.append({"m": m, "rs": rs})

    hurst_df = pd.DataFrame(hurst_vs_m, columns=["aggregation_level", "hurst_rs"])
    return hurst_df, rs_df, rs_agr


def self_similarity_rs_cloudy2(
    ac=None,
    flowID: int = 0,
    aggregation_levels: list[int] = [1, 5, 10, 50, 100, 500],
    synthetic_process_type: str = "self_similar",
    synthetic_hurst: float = 0.7,
):
    """
    Realiza a análise R/S (Range/Standard Deviation) e calcula o expoente de Hurst
    para dados de tráfego de internet, com a opção de gerar um gráfico "nuvem"
    e analisar o Hurst em diferentes níveis de agregação.

    Parâmetros:
    -----------
    ac : object, opcional
        Objeto que contém os dados de tráfego. Se None, dados sintéticos serão gerados.
    flowID : int, opcional
        ID do fluxo para filtrar os dados (se 'ac' for fornecido). Padrão é 0.
    aggregation_levels : list[int], opcional
        Lista de níveis de agregação (m) para os quais o expoente de Hurst será calculado.
        Padrão é [1, 5, 10, 50, 100, 500].
    synthetic_process_type : str, opcional
        Tipo de processo para gerar dados sintéticos ('exponential', 'pareto', 'self_similar').
        Usado apenas se 'ac' for None. Padrão é 'self_similar'.
    synthetic_hurst : float, opcional
        Expoente de Hurst desejado para dados sintéticos 'self_similar'.
        Usado apenas se 'ac' for None e `synthetic_process_type` for 'self_similar'. Padrão é 0.7.

    Retorna:
    --------
    tuple:
        - hurst_df : pandas.DataFrame
            DataFrame contendo os expoentes de Hurst calculados para cada nível de agregação.
        - rs_df_cloudy : pandas.DataFrame
            DataFrame contendo os pontos para o "cloudy R/S plot" (log(n) vs log(R/S)).
        - rs_agr : list
            Lista de dicionários, onde cada dicionário contém o nível de agregação (m)
            e o DataFrame R/S (rs_df) para aquele nível.
    """

    def _rs_analysis_on_series_cloudy(series, block_sizes):
        """
        Realiza a análise R/S em uma série temporal para gerar pontos para um "cloudy plot"
        e calcula o expoente de Hurst (inclinação da regressão linear).

        Parâmetros:
        -----------
        series : numpy.ndarray ou list
            A série temporal a ser analisada.
        block_sizes : list[int]
            Lista de tamanhos de bloco (n) a serem usados na análise R/S.

        Retorna:
        --------
        tuple:
            - rs_df : pandas.DataFrame
                DataFrame com os valores log(n) e log(R/S) para cada ponto calculado.
            - slope : float
                O expoente de Hurst (inclinação da linha de regressão). Retorna np.nan se
                não houver dados suficientes para a regressão.
        """
        log_ns, log_rss = [], []

        for n in block_sizes:
            if n >= len(series):
                continue

            # O 'step' cria blocos sobrepostos para gerar o "cloudy plot".
            # Para o cálculo tradicional do Hurst, geralmente se usam blocos disjuntos.
            step = max(1, n // 4)

            for start in range(0, len(series) - n + 1, step):
                block = series[start : start + n]
                mean = np.mean(block)
                dev = block - mean
                cum_dev = np.cumsum(dev)
                R = np.max(cum_dev) - np.min(cum_dev)
                S = np.std(block, ddof=1)  # ddof=1 para desvio padrão da amostra

                if S != 0:
                    rs = R / S
                    log_ns.append(np.log2(n))
                    log_rss.append(np.log2(rs))

        rs_df = pd.DataFrame({"log_n": log_ns, "log_rs": log_rss})

        slope = np.nan
        # Precisa de pelo menos 2 pontos únicos para a regressão linear.
        # Ajuste para garantir que não há erro se todos os log_n forem iguais.
        if not rs_df.empty and len(rs_df["log_n"].unique()) > 1:
            try:
                slope, _, _, _, _ = linregress(
                    rs_df["log_n"].values, rs_df["log_rs"].values
                )
            except ValueError:
                # Ocorre se, por exemplo, todos os log_n são o mesmo valor
                slope = np.nan

        return rs_df, slope

    # --- 1. Preparação dos Dados ---
    # Obtenção ou geração dos dados de inter-chegada de pacotes.
    if ac is None:
        # Agora usando os novos parâmetros para a função de geração de dados sintéticos
        df = _generate_synthetic_interarrival_df(
            n_packets=100000,  # Aumentei o número de pacotes para uma série mais longa
            process_type=synthetic_process_type,
            hurst=synthetic_hurst,
        )
    else:
        # Assumindo que get_packet_arrival_df retorna um DataFrame com 'timestamp' e 'pkt_size'
        df = get_packet_arrival_df(ac, flowID=flowID)

    # Binning dos dados: Agrega o tamanho dos pacotes em intervalos de tempo fixos.
    bin_width = 0.01  # Largura de cada "bin" de tempo em segundos
    time_start = df["timestamp"].min()
    time_end = df["timestamp"].max()
    # Usar `np.ceil` para garantir que o último bin seja incluído corretamente.
    bins = np.arange(time_start, time_end + bin_width, bin_width)
    df["time_bin"] = pd.cut(
        df["timestamp"], bins=bins, labels=False, include_lowest=True, right=False
    )
    bytes_per_bin = df.groupby("time_bin")["pkt_size"].sum().fillna(0).values

    # --- 2. Cloudy R/S Plot (Estilo Figura 2a) ---
    # Realiza a análise R/S para gerar os pontos dispersos do gráfico "nuvem".
    rs_df_cloudy, _ = _rs_analysis_on_series_cloudy(
        bytes_per_bin,
        block_sizes=[
            2**i for i in range(1, int(np.log2(len(bytes_per_bin))) - 2)
        ],  # Tamanhos de bloco dinâmicos
    )
    # Adiciona linhas de referência para slopes de 1.0 (tráfego browniano) e 0.5 (ruído branco).
    if not rs_df_cloudy.empty:
        x = rs_df_cloudy["log_n"]
        rs_df_cloudy["slope_1_line"] = x * 1.0
        rs_df_cloudy["slope_half_line"] = x * 0.5
    else:
        print(
            "Aviso: rs_df_cloudy está vazio, não é possível gerar linhas de referência."
        )

    # --- 3. Hurst vs Nível de Agregação (Estilo Figura 2d) ---
    # Calcula o expoente de Hurst para a série de tráfego em diferentes níveis de agregação.
    hurst_vs_m = []
    rs_agr = (
        []
    )  # Para armazenar os DataFrames R/S de cada nível de agregação, se necessário para plotagem.

    for m in aggregation_levels:
        # Garante que o comprimento da série é um múltiplo do nível de agregação.
        n = len(bytes_per_bin) // m
        if n == 0:
            # Não é possível agregar se 'm' for maior que o comprimento da série
            hurst_vs_m.append((m, np.nan))
            rs_agr.append({"m": m, "rs": pd.DataFrame()})
            continue

        truncated = bytes_per_bin[: n * m]

        # Agrega a série, calculando a média dos bytes por bin para cada bloco de tamanho 'm'.
        agg_series = truncated.reshape((n, m)).mean(axis=1)

        # Realiza a análise R/S na série agregada para obter o expoente de Hurst.
        # Os 'block_sizes' devem ser adequados para o comprimento da série agregada.
        # Definindo block_sizes dinamicamente para _rs_analysis_on_series_cloudy
        max_block_size = len(agg_series) // 4
        if max_block_size < 2:
            current_block_sizes = [2]  # Mínimo
        else:
            current_block_sizes = [
                2**i for i in range(1, int(np.log2(max_block_size)) + 1)
            ]
            if not current_block_sizes:  # Se max_block_size é muito pequeno
                current_block_sizes = [2] if len(agg_series) >= 2 else []

        rs_per_agg_df, hurst = _rs_analysis_on_series_cloudy(
            agg_series, block_sizes=current_block_sizes
        )
        hurst_vs_m.append((m, hurst))
        rs_agr.append(
            {"m": m, "rs": rs_per_agg_df}
        )  # Guarda o df R/S para cada m, se precisar plotar.

    # Converte os resultados do Hurst em um DataFrame para fácil visualização.
    hurst_df = pd.DataFrame(hurst_vs_m, columns=["aggregation_level", "hurst_rs"])

    return hurst_df, rs_df_cloudy, rs_agr


# --- 2. Função de Análise R/S para Cloudy Plot e Hurst vs Agregação (Figura 2a e 2d) ---
# Esta função pode ser colocada em um arquivo 'rs_analysis.py'.
def self_similarity_rs_cloudy3(
    ac=None, flowID: int = 0, aggregation_levels: list[int] = [1, 5, 10, 50, 100, 500]
):
    """
    Realiza a análise R/S (Range/Standard Deviation) para dados de tráfego de internet.

    Parâmetros:
    -----------
    ac : object, opcional
        Objeto que contém os dados de tráfego. Se None, dados sintéticos serão gerados.
    flowID : int, opcional
        ID do fluxo para filtrar os dados (se 'ac' for fornecido). Padrão é 0.
    aggregation_levels : list[int], opcional
        Lista de níveis de agregação (m) para os quais o expoente de Hurst será calculado.
        Padrão é [1, 5, 10, 50, 100, 500].

    Retorna:
    --------
    tuple:
        - hurst_df : pandas.DataFrame
            DataFrame contendo os expoentes de Hurst (via R/S) calculados para cada nível de agregação.
            Colunas: 'aggregation_level', 'hurst_rs'.
        - rs_df_cloudy : pandas.DataFrame
            DataFrame contendo os pontos para o "cloudy R/S plot" (log(n) vs log(R/S)).
            Colunas: 'log_n', 'log_rs', 'slope_1_line', 'slope_half_line'.
    """

    def _rs_analysis_on_series_cloudy_internal(series, block_sizes):
        log_ns, log_rss = [], []
        for n in block_sizes:
            if n >= len(series):
                continue
            step = max(1, n // 4)
            for start in range(0, len(series) - n + 1, step):
                block = series[start : start + n]
                mean = np.mean(block)
                dev = block - mean
                cum_dev = np.cumsum(dev)
                R = np.max(cum_dev) - np.min(cum_dev)
                S = np.std(block, ddof=1)
                if S != 0:
                    rs = R / S
                    log_ns.append(np.log2(n))
                    log_rss.append(np.log2(rs))

        rs_df = pd.DataFrame({"log_n": log_ns, "log_rs": log_rss})
        slope = np.nan
        if not rs_df.empty and len(rs_df["log_n"].unique()) > 1:
            try:
                slope, _, _, _, _ = linregress(
                    rs_df["log_n"].values, rs_df["log_rs"].values
                )
            except ValueError:
                slope = np.nan
        return rs_df, slope

    # --- 1. Preparação dos Dados ---
    if ac is None:
        df = _generate_synthetic_interarrival_df(
            n_packets=10000, process_type="self_similar", hurst=0.7
        )
    else:
        df = get_packet_arrival_df(ac, flowID=flowID)

    bytes_per_bin = _bin_packet_data(df)

    # --- 2. Cloudy R/S Plot (Estilo Figura 2a) ---
    rs_df_cloudy, _ = _rs_analysis_on_series_cloudy_internal(
        bytes_per_bin, block_sizes=[2, 4, 8, 16, 32, 64, 128]
    )
    if not rs_df_cloudy.empty:
        x = rs_df_cloudy["log_n"]
        rs_df_cloudy["slope_1_line"] = x * 1.0
        rs_df_cloudy["slope_half_line"] = x * 0.5
    else:
        print(
            "Aviso: rs_df_cloudy está vazio, não é possível gerar linhas de referência."
        )

    # --- 3. Hurst vs Nível de Agregação (Estilo Figura 2d) ---
    hurst_vs_m = []
    for m in aggregation_levels:
        n = len(bytes_per_bin) // m
        if n == 0:
            hurst_vs_m.append((m, np.nan))
            continue

        truncated = bytes_per_bin[: n * m]
        agg_series = truncated.reshape((n, m)).mean(axis=1)

        # Usando os block_sizes fornecidos por você para a série agregada
        _, hurst = _rs_analysis_on_series_cloudy_internal(
            agg_series, block_sizes=[2, 4, 8, 16, 32]
        )
        hurst_vs_m.append((m, hurst))

    hurst_df = pd.DataFrame(hurst_vs_m, columns=["aggregation_level", "hurst_rs"])

    return (
        hurst_df,
        rs_df_cloudy,
    )  # rs_agr não é mais retornado aqui para simplificar e focar nos plots finais.


# --- 3. Nova Função de Análise de Variância para Variance-Time Plot (Figura 2b) ---
# Esta função pode ser colocada em um arquivo 'variance_analysis.py'.
def self_similarity_variance_time(
    ac=None, flowID: int = 0, aggregation_levels: list[int] = [1, 5, 10, 50, 100, 500]
):
    """
    Realiza a análise de Variância para dados de tráfego de internet para gerar o Variance-Time Plot.

    Parâmetros:
    -----------
    ac : object, opcional
        Objeto que contém os dados de tráfego. Se None, dados sintéticos serão gerados.
    flowID : int, opcional
        ID do fluxo para filtrar os dados (se 'ac' for fornecido). Padrão é 0.
    aggregation_levels : list[int], opcional
        Lista de níveis de agregação (m) a serem usados para calcular a variância.
        Padrão é [1, 5, 10, 50, 100, 500].

    Retorna:
    --------
    tuple:
        - variance_df : pandas.DataFrame
            DataFrame contendo os pontos para o "Variance-Time Plot" (log2(m) vs log2(Variância)).
            Colunas: 'log_m', 'log_variance', 'regression_line'.
        - hurst_from_variance : float
            O expoente de Hurst calculado a partir da análise de variância.
    """

    def _variance_analysis_on_series_internal(series, aggregation_levels):
        log_ms = []
        log_variances = []

        for m in aggregation_levels:
            if m == 0 or m > len(series):
                continue

            truncated_len = (len(series) // m) * m
            if truncated_len == 0:
                continue

            agg_series = series[:truncated_len].reshape(-1, m).mean(axis=1)

            if len(agg_series) > 1:
                variance = np.var(agg_series, ddof=0)
                if variance > 0:
                    log_ms.append(np.log2(m))
                    log_variances.append(np.log2(variance))

        var_df = pd.DataFrame({"log_m": log_ms, "log_variance": log_variances})

        hurst_variance = np.nan
        if not var_df.empty and len(var_df["log_m"].unique()) > 1:
            try:
                slope, intercept, _, _, _ = linregress(
                    var_df["log_m"].values, var_df["log_variance"].values
                )
                hurst_variance = (slope + 2) / 2
                var_df["regression_line"] = slope * var_df["log_m"] + intercept
            except ValueError:
                hurst_variance = np.nan
                var_df["regression_line"] = np.nan

        return var_df, hurst_variance

    # --- 1. Preparação dos Dados ---
    if ac is None:
        df = _generate_synthetic_interarrival_df(
            n_packets=10000, process_type="self_similar", hurst=0.7
        )
    else:
        df = get_packet_arrival_df(ac, flowID=flowID)

    bytes_per_bin = _bin_packet_data(df)

    # --- 2. Realiza a Análise de Variância ---
    variance_df, hurst_from_variance = _variance_analysis_on_series_internal(
        bytes_per_bin, aggregation_levels=aggregation_levels
    )

    return variance_df, hurst_from_variance


##################################################


# --- 4. Funções de Plotagem Separadas ---
# Estas funções podem ser colocadas em um arquivo 'plot_functions.py'.


def plot_rs_cloudy(
    rs_df_cloudy, title="Cloudy R/S Plot", filename="rs_cloudy_plot.png"
):
    """
    Plota o gráfico "Cloudy R/S Plot" (log2(n) vs log2(R/S)).

    Parâmetros:
    -----------
    rs_df_cloudy : pandas.DataFrame
        DataFrame contendo os pontos para o plot, com 'log_n', 'log_rs',
        'slope_1_line', 'slope_half_line'.
    title : str, opcional
        Título do gráfico. Padrão é "Cloudy R/S Plot".
    filename : str, opcional
        Nome do arquivo para salvar o gráfico. Padrão é "rs_cloudy_plot.png".
    """
    plt.figure(figsize=(10, 7))
    plt.scatter(
        rs_df_cloudy["log_n"],
        rs_df_cloudy["log_rs"],
        alpha=0.3,
        s=10,
        label="Pontos R/S",
    )
    if not rs_df_cloudy.empty:
        plt.plot(
            rs_df_cloudy["log_n"],
            rs_df_cloudy["slope_1_line"],
            color="red",
            linestyle="--",
            label="H=1.0 (Brownian)",
        )
        plt.plot(
            rs_df_cloudy["log_n"],
            rs_df_cloudy["slope_half_line"],
            color="green",
            linestyle="--",
            label="H=0.5 (White Noise)",
        )
    plt.xlabel("log₂(n)")
    plt.ylabel("log₂(R/S)")
    plt.title(title)
    plt.legend()
    plt.grid(True, which="both", ls="--", c="0.7")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"Gráfico '{filename}' salvo com sucesso.")


def plot_hurst_aggregation(
    hurst_df,
    title="Expoente de Hurst vs Nível de Agregação",
    filename="hurst_aggregation_plot.png",
):
    """
    Plota o gráfico do Expoente de Hurst vs Nível de Agregação.

    Parâmetros:
    -----------
    hurst_df : pandas.DataFrame
        DataFrame contendo os expoentes de Hurst por nível de agregação, com 'aggregation_level', 'hurst_rs'.
    title : str, opcional
        Título do gráfico. Padrão é "Expoente de Hurst vs Nível de Agregação".
    filename : str, opcional
        Nome do arquivo para salvar o gráfico. Padrão é "hurst_aggregation_plot.png".
    """
    plt.figure(figsize=(10, 7))
    plt.plot(
        hurst_df["aggregation_level"],
        hurst_df["hurst_rs"],
        marker="o",
        label="Hurst R/S",
    )
    if not hurst_df.empty:
        avg_hurst = hurst_df["hurst_rs"].mean()
        plt.axhline(
            y=avg_hurst,
            color="purple",
            linestyle=":",
            label=f"Hurst R/S Médio: {avg_hurst:.2f}",
        )
    plt.xlabel("Nível de Agregação (m)")
    plt.ylabel("Expoente de Hurst (H)")
    plt.title(title)
    plt.grid(True, which="both", ls="--", c="0.7")
    plt.xscale("log")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"Gráfico '{filename}' salvo com sucesso.")


def plot_variance_time_plot(
    variance_df,
    hurst_from_variance,
    title="Variance-Time Plot",
    filename="variance_time_plot.png",
):
    """
    Plota o gráfico Variance-Time (log2(m) vs log2(Variância)).

    Parâmetros:
    -----------
    variance_df : pandas.DataFrame
        DataFrame contendo os pontos para o plot, com 'log_m', 'log_variance', 'regression_line'.
    hurst_from_variance : float
        O expoente de Hurst calculado a partir da análise de variância.
    title : str, opcional
        Título do gráfico. Padrão é "Variance-Time Plot".
    filename : str, opcional
        Nome do arquivo para salvar o gráfico. Padrão é "variance_time_plot.png".
    """
    plt.figure(figsize=(10, 7))
    plt.scatter(
        variance_df["log_m"],
        variance_df["log_variance"],
        alpha=0.7,
        s=30,
        label="Pontos Variância",
    )
    if not variance_df.empty and not np.isnan(hurst_from_variance):
        plt.plot(
            variance_df["log_m"],
            variance_df["regression_line"],
            color="blue",
            linestyle="-",
            label=f"Regressão (H={hurst_from_variance:.2f})",
        )
    plt.xlabel("log₂(m)")
    plt.ylabel("log₂(Variância)")
    plt.title(title)
    plt.legend()
    plt.grid(True, which="both", ls="--", c="0.7")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"Gráfico '{filename}' salvo com sucesso.")


#############################################


def test_calc_self_similarity_stats_gemini():
    print("Iniciando a análise de auto-similaridade com dados sintéticos...")

    # --- Exemplo com processo auto-similar (H ~ 0.7) ---
    print("\n--- Análise com processo auto-similar (Hurst ~ 0.7) ---")
    hurst_df_ss, rs_df_cloudy_ss, rs_agr_ss = self_similarity_rs_cloudy(ac=None)
    print("\nExpoente de Hurst por Nível de Agregação (Self-Similar):")
    print(hurst_df_ss)
    print("\nPrimeiras linhas do DataFrame para o Cloudy R/S Plot (Self-Similar):")
    print(rs_df_cloudy_ss.head())

    # --- Exemplo com processo exponencial (H ~ 0.5) ---
    print("\n--- Análise com processo exponencial (Hurst ~ 0.5) ---")
    hurst_df_exp, rs_df_cloudy_exp, rs_agr_exp = self_similarity_rs_cloudy2(
        ac=None, synthetic_process_type="exponential"
    )
    print("\nExpoente de Hurst por Nível de Agregação (Exponencial):")
    print(hurst_df_exp)
    print("\nPrimeiras linhas do DataFrame para o Cloudy R/S Plot (Exponencial):")
    print(rs_df_cloudy_exp.head())

    # --- Plotagem dos resultados (requer matplotlib) ---
    try:
        import matplotlib.pyplot as plt

        # Plot para o processo Auto-Similar
        fig1, axes1 = plt.subplots(1, 2, figsize=(16, 6))
        fig1.suptitle("Análise de Auto-Similaridade - Processo Auto-Similar (H~0.7)")

        # Plot 1: Cloudy R/S Plot (Self-Similar)
        axes1[0].scatter(
            rs_df_cloudy_ss["log_n"],
            rs_df_cloudy_ss["log_rs"],
            alpha=0.3,
            s=10,
            label="Pontos R/S",
        )
        if not rs_df_cloudy_ss.empty:
            axes1[0].plot(
                rs_df_cloudy_ss["log_n"],
                rs_df_cloudy_ss["slope_1_line"],
                color="red",
                linestyle="--",
                label="H=1.0 (Brownian)",
            )
            axes1[0].plot(
                rs_df_cloudy_ss["log_n"],
                rs_df_cloudy_ss["slope_half_line"],
                color="green",
                linestyle="--",
                label="H=0.5 (White Noise)",
            )
        axes1[0].set_xlabel("log₂(n)")
        axes1[0].set_ylabel("log₂(R/S)")
        axes1[0].set_title("Cloudy R/S Plot")
        axes1[0].legend()
        axes1[0].grid(True, which="both", ls="--", c="0.7")

        # Plot 2: Hurst vs Aggregation Level (Self-Similar)
        axes1[1].plot(
            hurst_df_ss["aggregation_level"],
            hurst_df_ss["hurst_rs"],
            marker="o",
            label="Hurst Calculado",
        )
        if not hurst_df_ss.empty:
            # Média do Hurst para referência
            avg_hurst = hurst_df_ss["hurst_rs"].mean()
            axes1[1].axhline(
                y=avg_hurst,
                color="purple",
                linestyle=":",
                label=f"Hurst Médio: {avg_hurst:.2f}",
            )
        axes1[1].set_xlabel("Nível de Agregação (m)")
        axes1[1].set_ylabel("Expoente de Hurst (H)")
        axes1[1].set_title("Expoente de Hurst vs Nível de Agregação")
        axes1[1].grid(True, which="both", ls="--", c="0.7")
        axes1[1].set_xscale("log")
        axes1[1].legend()

        # Plot para o processo Exponencial
        fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))
        fig2.suptitle("Análise de Auto-Similaridade - Processo Exponencial (H~0.5)")

        # Plot 1: Cloudy R/S Plot (Exponencial)
        axes2[0].scatter(
            rs_df_cloudy_exp["log_n"],
            rs_df_cloudy_exp["log_rs"],
            alpha=0.3,
            s=10,
            label="Pontos R/S",
        )
        if not rs_df_cloudy_exp.empty:
            axes2[0].plot(
                rs_df_cloudy_exp["log_n"],
                rs_df_cloudy_exp["slope_1_line"],
                color="red",
                linestyle="--",
                label="H=1.0 (Brownian)",
            )
            axes2[0].plot(
                rs_df_cloudy_exp["log_n"],
                rs_df_cloudy_exp["slope_half_line"],
                color="green",
                linestyle="--",
                label="H=0.5 (White Noise)",
            )
        axes2[0].set_xlabel("log₂(n)")
        axes2[0].set_ylabel("log₂(R/S)")
        axes2[0].set_title("Cloudy R/S Plot")
        axes2[0].legend()
        axes2[0].grid(True, which="both", ls="--", c="0.7")

        # Plot 2: Hurst vs Aggregation Level (Exponencial)
        axes2[1].plot(
            hurst_df_exp["aggregation_level"],
            hurst_df_exp["hurst_rs"],
            marker="o",
            label="Hurst Calculado",
        )
        if not hurst_df_exp.empty:
            avg_hurst_exp = hurst_df_exp["hurst_rs"].mean()
            axes2[1].axhline(
                y=avg_hurst_exp,
                color="purple",
                linestyle=":",
                label=f"Hurst Médio: {avg_hurst_exp:.2f}",
            )
        axes2[1].set_xlabel("Nível de Agregação (m)")
        axes2[1].set_ylabel("Expoente de Hurst (H)")
        axes2[1].set_title("Expoente de Hurst vs Nível de Agregação")
        axes2[1].grid(True, which="both", ls="--", c="0.7")
        axes2[1].set_xscale("log")
        axes2[1].legend()

        plt.tight_layout(
            rect=[0, 0.03, 1, 0.95]
        )  # Ajusta layout para evitar sobreposição de títulos
        plt.savefig("gemini_hurst_rs.png")

    except ImportError:
        print(
            "\nMatplotlib não está instalado. Não é possível gerar os gráficos de exemplo."
        )
        print("Instale com: pip install matplotlib")

    print("\nAnálise concluída.")


def test_calc_self_similarity_stats_as_df():
    # hurst_df, rs_df, rs_agr = self_similarity_rs_cloudy(ac=None)
    hurst_df, rs_df, rs_agr = self_similarity_rs_cloudy2(ac=None)

    # --- Plot 1: Cloudy R/S ---
    plt.figure(figsize=(10, 6))
    plt.scatter(
        rs_df["log_n"], rs_df["log_rs"], alpha=0.4, s=15, label="R/S values", marker="+"
    )
    plt.plot(
        rs_df["log_n"],
        rs_df["slope_1_line"],
        linestyle="--",
        color="gray",
        label="slope = 1.0",
    )
    plt.plot(
        rs_df["log_n"],
        rs_df["slope_half_line"],
        linestyle="--",
        color="black",
        label="slope = 0.5",
    )
    plt.title("R/S Analysis with Multiple Windows (Cloudy Plot)")
    plt.xlabel("log(Block Size)")
    plt.ylabel("log(R/S)")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("rs_cloudy_plot.png")

    # --- Plot 2: Hurst vs Aggregation Level ---
    plt.figure(figsize=(8, 5))
    plt.plot(
        hurst_df["aggregation_level"], hurst_df["hurst_rs"], marker="o", linestyle="-"
    )
    plt.axhline(y=0.5, color="gray", linestyle="--", label="H = 0.5 (no correlation)")
    plt.axhline(y=1.0, color="black", linestyle="--", label="H = 1.0 (strong LRD)")
    plt.xscale("log")
    plt.xlabel("Aggregation Level (m)")
    plt.ylabel("Estimated Hurst Exponent")
    plt.title("Hurst vs Aggregation Level")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("hurst_vs_aggregation.png")


def test_self_similarity_stats_gemini2():
    print("Iniciando a análise de auto-similaridade com dados sintéticos...")

    # --- Análise para Processo Auto-Similar (H ~ 0.7) ---
    print("\n--- Processo Auto-Similar (Hurst ~ 0.7) ---")

    # Chamada para a análise R/S
    hurst_df_ss, rs_df_cloudy_ss = self_similarity_rs_cloudy3(ac=None)
    print("\nExpoente de Hurst (R/S) por Nível de Agregação (Self-Similar):")
    print(hurst_df_ss)

    # Chamada para a análise de Variância
    variance_df_ss, hurst_var_ss = self_similarity_variance_time(ac=None)
    print(
        f"\nExpoente de Hurst (Variância) para processo Self-Similar: {hurst_var_ss:.4f}"
    )

    # Plotagem para Processo Auto-Similar
    plot_rs_cloudy(
        rs_df_cloudy_ss,
        title="Figura 2a: Cloudy R/S Plot (Self-Similar, H~0.7)",
        filename="figure_2a_rs_cloudy_self_similar.png",
    )
    plot_hurst_aggregation(
        hurst_df_ss,
        title="Figura 2d: Hurst vs Agregação (Self-Similar, H~0.7)",
        filename="figure_2d_hurst_aggregation_self_similar.png",
    )
    plot_variance_time_plot(
        variance_df_ss,
        hurst_var_ss,
        title=f"Figura 2b: Variance-Time Plot (Self-Similar, H~{hurst_var_ss:.2f})",
        filename="figure_2b_variance_time_self_similar.png",
    )


if __name__ == "__main__":
    # calc_self_similarity_stats_as_df(None)
    # test_calc_self_similarity_stats_as_df()'
    # test_calc_self_similarity_stats_as_df()
    # test_calc_self_similarity_stats_as_df_2()
    # test_calc_self_similarity_stats_gemini()
    test_self_similarity_stats_gemini2()
