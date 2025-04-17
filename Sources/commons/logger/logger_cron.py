import logging
import time


class LoggerCron:
    def __init__(self, logger: logging.Logger, label=""):
        self.logger = logger
        self.start = time.time()
        self.stopped = False
        self.label = label

    def stop(self):
        if self.stopped:
            return
        
        end = time.time()
        duration = end - self.start
        self.logger.debug(f"{self.label}| It took {duration:.6f} seconds to finish the cronometer.")
        self.stopped = True

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("CronLogger")
    
    cron = LoggerCron(logger)
    time.sleep(2)
    cron.stop()
