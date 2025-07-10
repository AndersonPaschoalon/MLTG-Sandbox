import numpy as np
import pandas as pd
from fbm import FBM

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
            "time": timestamps,
            "inter_arrival": inter_arrivals,
            "pkt_size": pkt_sizes,
            "ttl": 64,  # TTL padrão para pacotes IP
        }
    )

    return df


def calc_bw_pps_fps_as_df(
    connector: AlchemyConnector, flowID: int = 0, time_granularity: float = 0.1
) -> pd.DataFrame:
    """
    Calculates the bandwidth for a given flow (or all flows) over time.

    Args:
        connector: An instantiated AlchemyConnector to the database.
        flowID: The ID of the flow to analyze. If <= 0, analyzes all flows together.
        time_granularity: The time interval (in seconds) for calculating bandwidth.

    Returns:
        A pandas DataFrame with columns:
        - point_count: sequence number of the time point,
        - time: time point in seconds,
        - bandwidth: bandwidth at the time point,
        - bandwidth_average: average bandwidth over the entire period,
        - bandwidth_variance: variance of the bandwidth over the entire period,
        - npackets: number of packets at the time point,
        - npackets_average: average number of packets over the entire period,
        - npackets_variance: variance of the number of packets over the entire period,
        - nflows: number of flows at the time point,
        - nflows_average: average number of flows over the entire period,
        - nflows_variance: variance of the number of flows over the entire period.
    """
    if time_granularity <= 0:
        raise ValueError("Time granularity must be greater than 0")

    with connector.session() as session:
        if flowID > 0:
            packets = (
                session.query(Packet)
                .filter(Packet.flowID == flowID)
                .order_by(Packet.tsSec, Packet.tsUsec)
                .all()
            )
            flows_in_period = 1
        else:
            packets = session.query(Packet).order_by(Packet.tsSec, Packet.tsUsec).all()
            flows_in_period = session.query(Packet.flowID).distinct().count()

        if not packets:
            return pd.DataFrame(
                {
                    "point_count": [],
                    "time": [],
                    "bandwidth": [],
                    "bandwidth_average": [],
                    "bandwidth_variance": [],
                    "npackets": [],
                    "npackets_average": [],
                    "npackets_variance": [],
                    "nflows": [],
                    "nflows_average": [],
                    "nflows_variance": [],
                }
            )

        timestamps = [p.timestamp_seconds for p in packets]
        packet_sizes = [p.pktSize for p in packets]
        flow_ids = [p.flowID for p in packets]

        max_time = max(timestamps)
        time_points = np.arange(0, max_time + time_granularity, time_granularity)
        num_time_points = len(time_points) - 1

        # Compute nflows per interval
        if flows_in_period > 1:
            interval_flows = [
                {
                    flow_id
                    for ts, flow_id in zip(timestamps, flow_ids)
                    if start <= ts < end
                }
                for start, end in zip(time_points[:-1], time_points[1:])
            ]
            nflows_per_interval = [len(fset) for fset in interval_flows]
        else:
            nflows_per_interval = [1] * num_time_points

        bandwidth_data = []
        packet_counts = []

        for i in range(num_time_points):
            start_time = time_points[i]
            end_time = time_points[i + 1]
            interval_packets = [
                size
                for ts, size in zip(timestamps, packet_sizes)
                if start_time <= ts < end_time
            ]
            interval_bandwidth = sum(interval_packets) * 8 / time_granularity
            bandwidth_data.append(interval_bandwidth)
            packet_counts.append(len(interval_packets))
        # bw
        avg_bandwidth = np.mean(bandwidth_data)
        bw_variance = np.var(bandwidth_data) if num_time_points > 1 else 0
        # pps
        avg_packet_count = np.mean(packet_counts)
        packet_count_variance = np.var(packet_counts) if num_time_points > 1 else 0
        # time
        midpoint_times = time_points[:-1] + time_granularity / 2
        # fps
        avg_nflows = np.mean(nflows_per_interval)
        flow_count_variance = np.var(nflows_per_interval) if num_time_points > 1 else 0

        df = pd.DataFrame(
            {
                "point_count": range(1, num_time_points + 1),
                "time": midpoint_times,
                "bandwidth": bandwidth_data,
                "bandwidth_average": [avg_bandwidth] * num_time_points,
                "bandwidth_variance": [bw_variance] * num_time_points,
                "npackets": packet_counts,
                "npackets_average": [avg_packet_count] * num_time_points,
                "npackets_variance": [packet_count_variance] * num_time_points,
                "nflows": nflows_per_interval,
                "nflows_average": [avg_nflows] * num_time_points,
                "nflows_variance": [flow_count_variance] * num_time_points,
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


def get_bandwidth_signal(
    ac, flowID=0, bin_width: float = 0.01, agg: str = "count"
) -> np.ndarray:
    """
    Generate a uniformly sampled time-series signal representing either
    packet counts or bandwidth (bytes) over fixed-width time bins.

    Parameters:
    -----------
    ac : AlchemyConnector
        Database connection object to retrieve packet data.

    flowID : int, default=0
        Flow ID to filter packets. If 0 or negative, all flows are used.

    bin_width : float, default=0.01
        Width of each time bin in seconds. Used to discretize the timeline.

    agg : str, default='count'
        Aggregation method:
            - "count": Number of packets per bin (i.e., packet rate).
            - "sum": Total packet size per bin (i.e., bandwidth in bytes).

    Returns:
    --------
    np.ndarray
        1D NumPy array representing the signal (packet count or bandwidth) per time bin.
        Missing bins (i.e., with no packets) are filled with zero.

    Raises:
    -------
    ValueError:
        - If no packet data is found for the specified flowID.
        - If required DataFrame columns are missing.
        - If aggregation method is invalid.
    """
    # --- Step 1: Load packet data ---
    if not ac:
        df = _generate_synthetic_interarrival_df()
    else:
        df = get_packet_arrival_df(ac, flowID=flowID)

    if df.empty:
        raise ValueError(f"No packets found for flowID={flowID}.")

    required_cols = {"time", "pkt_size"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_cols - set(df.columns)}")

    # --- Step 2: Bin time values into fixed-size intervals ---
    time_start = df["time"].min()
    time_end = df["time"].max()

    num_bins = int(np.ceil((time_end - time_start) / bin_width)) + 1
    bin_edges = np.linspace(
        time_start, time_start + num_bins * bin_width, num=num_bins + 1
    )

    df["time_bin"] = pd.cut(
        df["time"], bins=bin_edges, labels=False, include_lowest=True
    )

    # --- Step 3: Aggregate by chosen method ---
    if agg == "count":
        values = df.groupby("time_bin").size()
    elif agg == "sum":
        values = df.groupby("time_bin")["pkt_size"].sum()
    else:
        raise ValueError("agg must be either 'count' or 'sum'.")

    # --- Step 4: Fill gaps with zero (ensures all bins are present) ---
    signal = np.zeros(num_bins)
    signal[values.index.astype(int)] = values.values

    # --- Step 5: Filter non-finite values just in case ---
    signal = signal[np.isfinite(signal)]

    return signal
