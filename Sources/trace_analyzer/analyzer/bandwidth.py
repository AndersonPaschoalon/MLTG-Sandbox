import numpy as np
import pandas as pd
from sqlalchemy import TEXT, Column, ForeignKey, Integer, create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from commons.connectors.alchemy_connector import AlchemyConnector
from commons.models.packet import Packet


def calc_bw_pps_fps(
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

        avg_bandwidth = np.mean(bandwidth_data)
        bw_variance = np.var(bandwidth_data) if num_time_points > 1 else 0
        avg_packet_count = np.mean(packet_counts)
        packet_count_variance = np.var(packet_counts) if num_time_points > 1 else 0
        flow_count_variance = np.var(nflows_per_interval) if num_time_points > 1 else 0
        midpoint_times = time_points[:-1] + time_granularity / 2

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
                "nflows_average": [flows_in_period] * num_time_points,
                "nflows_variance": [flow_count_variance] * num_time_points,
            }
        )

        return df
