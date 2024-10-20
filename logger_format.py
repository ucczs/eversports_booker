import logging

class EversportsLogger(logging.Formatter):
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s | %(name)-18s | %(levelname)-7s | %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)



def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    log_format = '%(asctime)s | %(name)-10s | %(levelname)-10s | %(message)s'

    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.ERROR)
    stdout_handler.setFormatter(EversportsLogger(log_format))


    logger.addHandler(stdout_handler)

    return logger