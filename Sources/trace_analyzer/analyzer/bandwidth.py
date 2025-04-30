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
        A pandas DataFrame with columns: point count, time, bandwidth, average bandwidth,
        bw variance, packet count, average packet count, packet count variance,
        number of flows, number of flows average, number of flows variance.
    """
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
            unique_flow_ids = session.query(Packet.flowID).distinct().scalar()
            flows_in_period = unique_flow_ids if unique_flow_ids is not None else 0

        if not packets:
            return pd.DataFrame(
                {
                    "point count": [],
                    "time": [],
                    "bandwidth": [],
                    "average bandwidth": [],
                    "bw variance": [],
                    "packet count": [],
                    "average packet count": [],
                    "packet count variance": [],
                    "number of flows": [],
                    "number of flows average": [],
                    "number of flows variance": [],
                }
            )

        timestamps = [p.timestamp_seconds for p in packets]
        packet_sizes = [p.pktSize for p in packets]

        if not timestamps:
            return pd.DataFrame(
                {
                    "point count": [],
                    "time": [],
                    "bandwidth": [],
                    "average bandwidth": [],
                    "bw variance": [],
                    "packet count": [],
                    "average packet count": [],
                    "packet count variance": [],
                    "number of flows": [],
                    "number of flows average": [],
                    "number of flows variance": [],
                }
            )

        max_time = max(timestamps) if timestamps else 0
        time_points = np.arange(0, max_time + time_granularity, time_granularity)
        bandwidth_data = []
        packet_counts = []

        for i in range(len(time_points) - 1):
            start_time = time_points[i]
            end_time = time_points[i + 1]
            interval_packets = [
                size
                for ts, size in zip(timestamps, packet_sizes)
                if start_time <= ts < end_time
            ]
            interval_bandwidth = (
                sum(interval_packets) * 8 / time_granularity
                if time_granularity > 0
                else 0
            )  # bits per second
            bandwidth_data.append(interval_bandwidth)
            packet_counts.append(len(interval_packets))

        avg_bandwidth = np.mean(bandwidth_data) if bandwidth_data else 0
        bw_variance = np.var(bandwidth_data) if len(bandwidth_data) > 1 else 0
        avg_packet_count = np.mean(packet_counts) if packet_counts else 0
        packet_count_variance = np.var(packet_counts) if len(packet_counts) > 1 else 0

        num_time_points = len(time_points) - 1
        df = pd.DataFrame(
            {
                "point count": range(1, num_time_points + 1),
                "time": time_points[:-1]
                + time_granularity / 2,  # Use midpoint of the interval
                "bandwidth": bandwidth_data,
                "average bandwidth": [avg_bandwidth] * num_time_points,
                "bw variance": [bw_variance] * num_time_points,
                "packet count": packet_counts,
                "average packet count": [avg_packet_count] * num_time_points,
                "packet count variance": [packet_count_variance] * num_time_points,
                "number of flows": [flows_in_period] * num_time_points,
                "number of flows average": [flows_in_period] * num_time_points,
                "number of flows variance": [0]
                * num_time_points,  # Variance of a constant is 0
            }
        )

        return df
