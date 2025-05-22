import numpy as np
import pandas as pd
from sqlalchemy import TEXT, Column, ForeignKey, Integer, create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from commons.connectors.alchemy_connector import AlchemyConnector
from commons.models.packet import Packet


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


def calc_urst_metrics(target: str, ac: AlchemyConnector, inter_arrival_threshold=0.01):
    """
    Analyze bursts for a given target and DB connector.

    - Burst: sequence of packets where inter-arrival < threshold.
    """

    print(f"[burst] Analyzing bursts for target: {target}")

    df = get_packet_arrival_df(ac)  # Assumes df has 'time' column
    df = df.sort_values("time").reset_index(drop=True)

    if df.empty or len(df) < 2:
        print(f"[WARN] Not enough packets for burst analysis: {target}")
        return

    # Calculate inter-arrival times
    df["inter_arrival"] = df["time"].diff().fillna(0)

    # Detect bursts
    bursts = []
    current_burst = [df.iloc[0]]
    for i in range(1, len(df)):
        if df["inter_arrival"].iloc[i] < inter_arrival_threshold:
            current_burst.append(df.iloc[i])
        else:
            bursts.append(pd.DataFrame(current_burst))
            current_burst = [df.iloc[i]]
    if current_burst:
        bursts.append(pd.DataFrame(current_burst))

    # Compute metrics
    burst_sizes = [len(burst) for burst in bursts]
    burst_durations = [
        burst["time"].iloc[-1] - burst["time"].iloc[0] for burst in bursts
    ]
    inter_burst_intervals = [
        bursts[i]["time"].iloc[0] - bursts[i - 1]["time"].iloc[-1]
        for i in range(1, len(bursts))
    ]

    # Filter valid values
    burst_sizes = [x for x in burst_sizes if x > 0 and np.isfinite(x)]
    burst_durations = [x for x in burst_durations if x > 0 and np.isfinite(x)]
    inter_burst_intervals = [
        x for x in inter_burst_intervals if x > 0 and np.isfinite(x)
    ]

    return burst_sizes, burst_durations, inter_burst_intervals
