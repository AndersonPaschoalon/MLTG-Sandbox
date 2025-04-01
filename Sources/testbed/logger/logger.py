import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class Logger:
    """
    Simple single thread singleton logger class.
    """
    LOGGER_NAME = "PyLogger"
    FORMAT_CONSOLE = '%(levelname)s - %(message)s'
    FORMAT_LOGFILE = '%(asctime)s - %(levelname)s - %(filename)s - Line: %(lineno)d - %(message)s'
    _rotating_method = 1  # 0 - single file | 1 = time rotating
    _backup_count = 50
    _logger = None
    _log_file = ""
    _log_path = ""

    @staticmethod
    def initialize(log_file, level_log=logging.DEBUG, level_console=logging.WARNING):
        """
        Initializes the singleton object.

        Args:
            log_file (str): The filename where the logs are going to be saved.
            level_log (int): Log level for the log file.
            level_console (int): Log level for the console.
            mode (int): On develop mode, it it is not initialized it should default configurations. On PRODUCTION
                should only intantiate configured intance to avoid not configured log files. 

        Returns:
            None
        """
        if Logger._logger:
            Logger._logger.warning(f"Logger {Logger.LOGGER_NAME} already initialized. New log file {log_file} will not be created.")
            return
        _log_file = log_file
        
        # Convert to absolute path and ensure directory exists
        log_path = Path(log_file).absolute()
        _log_path = log_path
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure the file is writable
        log_path.touch(mode=0o666, exist_ok=True)        

        Logger._logger = logging.getLogger(Logger.LOGGER_NAME)
        Logger._logger.setLevel(level_log)
        # create file handler which logs even debug messages
        fh = logging.FileHandler(log_file)
        if Logger._rotating_method == 1:
            fh = TimedRotatingFileHandler(log_file,
                                          when='midnight',
                                          backupCount=Logger._backup_count)
        fh.setLevel(level_log)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(level_console)
        # create formatter and add it to the handlers
        fh_formatter = logging.Formatter(Logger.FORMAT_LOGFILE)
        ch_formatter = logging.Formatter(Logger.FORMAT_CONSOLE)
        fh.setFormatter(fh_formatter)
        ch.setFormatter(ch_formatter)
        # add the handlers to logger
        Logger._logger.addHandler(ch)
        Logger._logger.addHandler(fh)
        Logger._logger.propagate = False
        # init log
        Logger._logger.info("-----------------------------------")
        Logger._logger.info("Log system successfully initialised")
        Logger._logger.info("-----------------------------------")
        #_mode = mode

    @staticmethod
    def get():
        """
        Returns the logger object.

        Raises: 
            AssertionError: if logger was not initialized.
        """
        assert Logger._logger is not None, "Error: get() was called before Logger was initialized. Call Logger.initialize() to use the logger."
        return Logger._logger

    @staticmethod
    def log_file() -> str:
        return Logger._log_file
    
    @staticmethod
    def log_dir() -> str:
        return Logger._log_path


        


