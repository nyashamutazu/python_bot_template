from dataclasses import dataclass


from dataclasses import dataclass
from typing import Optional

@dataclass
class Logging:
    name: str
    log_file_path: str

@dataclass
class CloudLogging:
    enabled: bool

@dataclass
class LoggingConfig:
    directories: dict
    cloud_logging: Optional[CloudLogging]  # Cloud logging is optional