from dataclasses import dataclass


@dataclass
class Logging:
    name: str
    log_file_path: str
    
    