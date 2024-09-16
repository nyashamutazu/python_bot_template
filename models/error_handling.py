from dataclasses import dataclass


@dataclass
class ErrorHandling:
    on_error: str
    max_retries: int
    logging_name: str
