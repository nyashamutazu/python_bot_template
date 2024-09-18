import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
import logging
import os

LOG_FORMAT = "%(asctime)s %(message)s"
DEFAULT_LEVEL = logging.DEBUG

class LogWrapper:
    PATH = './logs'

    def __init__(self, name, mode="w", cloud_logging_enabled=False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(DEFAULT_LEVEL)

        if cloud_logging_enabled:
            self.setup_cloud_logging(name)
        else:
            self.setup_file_logging(name, mode)

        self.logger.info(f"LogWrapper initialized for {name}")

    def setup_cloud_logging(self, name):
        client = google.cloud.logging.Client()
        cloud_handler = CloudLoggingHandler(client, name=name)
        formatter = logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        cloud_handler.setFormatter(formatter)
        self.logger.addHandler(cloud_handler)
        self.logger.info("Google Cloud Logging enabled")

    def setup_file_logging(self, name, mode):
        self.create_directory()
        self.filename = f"{LogWrapper.PATH}/{name}.log"
        file_handler = logging.FileHandler(self.filename, mode=mode)
        formatter = logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def create_directory(self):
        if not os.path.exists(LogWrapper.PATH):
            os.makedirs(LogWrapper.PATH)
