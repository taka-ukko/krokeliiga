import logging


class Logger:
    def __init__(self, log_path):
        # Enable logging
        logger = logging.getLogger('krokebot')
        logger.setLevel(logging.DEBUG)

        # Create file handler for logs
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)

        # Create stream handler to output errors to console
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                                      '%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        self.logger = logger
