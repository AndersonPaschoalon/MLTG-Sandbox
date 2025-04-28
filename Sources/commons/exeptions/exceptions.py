class PCAPNotFoundError(Exception):
    """PCAP file missing or inaccessible"""

    def __init__(self, pcap_file):
        self.pcap_file = pcap_file

    def __repr__(self):
        return f"PCAP {self.pcap_file} not found or inaccessible."


class InvalidPCAPError(Exception):
    """Malformed or unsupported PCAP"""

    def __init__(self, pcap_file, detail):
        self.pcap_file = pcap_file
        self.detail = detail

    def __repr__(self):
        return f"Invalid PCAP file {self.pcap_file}. {self.detail}"
