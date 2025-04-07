class NetworkExperimentError(Exception):
    """Base exception for all custom exceptions"""
    def __init__(self, message="Network experiment error occurred"):
        self.message = message
        super().__init__(self.message)

# --------------------------
# Configuration Exceptions
# --------------------------
class InvalidArgumentError(NetworkExperimentError):
    """Invalid parameter/value combination"""
    def __init__(self, param_name, value, valid_options=None):
        msg = f"Invalid value '{value}' for parameter '{param_name}'"
        if valid_options:
            msg += f". Valid options: {valid_options}"
        super().__init__(msg)
        self.param_name = param_name
        self.value = value

class MissingConfigError(NetworkExperimentError):
    """Required configuration missing"""
    def __init__(self, config_key):
        super().__init__(f"Missing required configuration: {config_key}")
        self.config_key = config_key

# --------------------------
# File/IO Exceptions  
# --------------------------
class ExperimentFileError(NetworkExperimentError):
    """Base for file-related errors"""
    def __init__(self, filepath, message="File operation failed"):
        super().__init__(f"{message} | File: {filepath}")
        self.filepath = filepath

class PCAPNotFoundError(ExperimentFileError):
    """PCAP file missing or inaccessible"""
    def __init__(self, pcap_path):
        super().__init__(
            filepath=pcap_path,
            message="PCAP file not found or inaccessible"
        )

class InvalidPCAPError(ExperimentFileError):
    """Malformed or unsupported PCAP"""
    def __init__(self, pcap_path, details):
        super().__init__(
            filepath=pcap_path,
            message=f"Invalid PCAP format: {details}"
        )

# --------------------------
# Network/Protocol Exceptions
# --------------------------
class ControllerError(NetworkExperimentError):
    """Controller communication failure"""
    def __init__(self, controller_type, port, details=""):
        super().__init__(
            f"Controller '{controller_type}' failed on port {port}. {details}"
        )
        self.controller_type = controller_type
        self.port = port

class TrafficGenerationError(NetworkExperimentError):
    """Traffic generator failure"""
    def __init__(self, generator_type, flow_details):
        super().__init__(
            f"Traffic generator '{generator_type}' failed during: {flow_details}"
        )
        self.generator_type = generator_type

class TopologyError(NetworkExperimentError):
    """Topology construction/validation failure""" 
    def __init__(self, topology_type, reason):
        super().__init__(
            f"Topology '{topology_type}' invalid: {reason}"
        )
        self.topology_type = topology_type