from enum import IntEnum

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from commons.connectors.base import Base


class NetworkProtocol(IntEnum):
    NONE = 0
    IPv4 = 1
    IPv6 = 2
    ARP = 3
    RARP = 4
    LOOPBACK = 5
    WOL = 6
    ATA = 7


class TransportProtocol(IntEnum):
    NONE = 0
    TCP = 1
    UDP = 2
    ICMP = 3
    ICMPv6 = 4
    DCCP = 5
    SCTP = 6
    IGMP = 7


class ApplicationProtocol(IntEnum):
    NONE = 0
    BGP = 1
    DHCP = 2
    DNS = 3
    FTP = 4
    IMAP = 5
    HTTP = 6
    HTTPS = 7
    MDNS = 8
    NTP = 9
    POP3 = 10
    QUIC = 11
    RTP = 12
    SSDP = 13
    SIP = 14
    SSH = 15
    SNMP = 16
    SMTP = 17
    SMTPS = 18
    Telnet = 19
    TFTP = 20
    TLS_SSL = 21


# Network Protocol Strings
_network_proto_names = {
    NetworkProtocol.NONE: "NONE",
    NetworkProtocol.IPv4: "IPv4",
    NetworkProtocol.IPv6: "IPv6",
    NetworkProtocol.ARP: "ARP",
    NetworkProtocol.RARP: "RARP",
    NetworkProtocol.LOOPBACK: "LOOPBACK",
    NetworkProtocol.WOL: "WOL",
    NetworkProtocol.ATA: "ATA",
}

# Transport Protocol Strings
_transport_proto_names = {
    TransportProtocol.NONE: "NONE",
    TransportProtocol.TCP: "TCP",
    TransportProtocol.UDP: "UDP",
    TransportProtocol.ICMP: "ICMP",
    TransportProtocol.ICMPv6: "ICMPv6",
    TransportProtocol.DCCP: "DCCP",
    TransportProtocol.SCTP: "SCTP",
    TransportProtocol.IGMP: "IGMP",
}

# Application Protocol Strings
_app_proto_names = {
    ApplicationProtocol.NONE: "NONE",
    ApplicationProtocol.BGP: "BGP",
    ApplicationProtocol.DHCP: "DHCP",
    ApplicationProtocol.DNS: "DNS",
    ApplicationProtocol.FTP: "FTP",
    ApplicationProtocol.IMAP: "IMAP",
    ApplicationProtocol.HTTP: "HTTP",
    ApplicationProtocol.HTTPS: "HTTPS",
    ApplicationProtocol.MDNS: "MDNS",
    ApplicationProtocol.NTP: "NTP",
    ApplicationProtocol.POP3: "POP3",
    ApplicationProtocol.QUIC: "QUIC",
    ApplicationProtocol.RTP: "RTP",
    ApplicationProtocol.SSDP: "SSDP",
    ApplicationProtocol.SIP: "SIP",
    ApplicationProtocol.SSH: "SSH",
    ApplicationProtocol.SNMP: "SNMP",
    ApplicationProtocol.SMTP: "SMTP",
    ApplicationProtocol.SMTPS: "SMTPS",
    ApplicationProtocol.Telnet: "Telnet",
    ApplicationProtocol.TFTP: "TFTP",
    ApplicationProtocol.TLS_SSL: "TLS/SSL",
}


class Flow(Base):
    __tablename__ = "Flows"

    flowID = Column(Integer, primary_key=True)
    traceID = Column(Integer, primary_key=True)
    stack = Column(String)
    portDstSrc = Column(String)
    net4DstSrcSumm = Column(String)
    net6DstSrc = Column(String)
    numberOfPackets = Column(Integer)

    # Derived properties (no DB storage)
    @property
    def port_src(self) -> int:
        """Extracts source port from portDstSrc (LSB 16 bits)"""
        if not self.portDstSrc:
            return 0
        port_pair = int(self.portDstSrc)
        return port_pair & 0xFFFF

    @property
    def port_dst(self) -> int:
        """Extracts destination port from portDstSrc (MSB 16 bits)"""
        if not self.portDstSrc:
            return 0
        port_pair = int(self.portDstSrc)
        return (port_pair >> 16) & 0xFFFF

    @property
    def ipv4_src(self) -> str:
        """Converts net4DstSrcSumm to dotted-decimal source IP"""
        if not self.net4DstSrcSumm:
            return ""
        ip_pair = int(self.net4DstSrcSumm)
        src_ip = ip_pair & 0xFFFFFFFF
        return f"{(src_ip >> 24) & 0xFF}.{(src_ip >> 16) & 0xFF}.{(src_ip >> 8) & 0xFF}.{src_ip & 0xFF}"

    @property
    def ipv4_dst(self) -> str:
        """Converts net4DstSrcSumm to dotted-decimal destination IP"""
        if not self.net4DstSrcSumm:
            return ""
        ip_pair = int(self.net4DstSrcSumm)
        dst_ip = (ip_pair >> 32) & 0xFFFFFFFF
        return f"{(dst_ip >> 24) & 0xFF}.{(dst_ip >> 16) & 0xFF}.{(dst_ip >> 8) & 0xFF}.{dst_ip & 0xFF}"

    @property
    def network_protocol(self) -> NetworkProtocol:
        """Extracts network protocol code (no string conversion)"""
        if not self.stack:
            return NetworkProtocol.NONE
        return NetworkProtocol((int(self.stack) >> 16) & 0xFF)

    @property
    def transport_protocol(self) -> TransportProtocol:
        """Extracts transport protocol code (no string conversion)"""
        if not self.stack:
            return TransportProtocol.NONE
        return TransportProtocol((int(self.stack) >> 8) & 0xFF)

    @property
    def application_protocol(self) -> ApplicationProtocol:
        """Extracts application protocol code (no string conversion)"""
        if not self.stack:
            return ApplicationProtocol.NONE
        return ApplicationProtocol(int(self.stack) & 0xFF)

    # String versions (lazy-loaded)
    @property
    def network_protocol_str(self) -> str:
        return _network_proto_names.get(self.network_protocol, "UNKNOWN")

    @property
    def transport_protocol_str(self) -> str:
        return _transport_proto_names.get(self.transport_protocol, "UNKNOWN")

    @property
    def application_protocol_str(self) -> str:
        return _app_proto_names.get(self.application_protocol, "UNKNOWN")
