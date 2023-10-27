import logging
import os

class LoggerConfigurator:
    _instances = {}

    def __new__(cls, logger_name, log_level, log_directory):
        if logger_name not in cls._instances:
            cls._instances[logger_name] = super(LoggerConfigurator, cls).__new__(cls)
            logger = cls._instances[logger_name].configure_logger(logger_name, log_level, log_directory)
            cls._instances[logger_name].logger = logger
        return cls._instances[logger_name]

    def configure_logger(self, logger_name, log_level, log_directory):
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Create file handler
        log_file = os.path.join(log_directory, f"{logger_name}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

if __name__ == "__main__":
    # Example usage:
    logger_config = LoggerConfigurator("testLogger", logging.DEBUG, "./logs")
    logger = logger_config.logger

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")