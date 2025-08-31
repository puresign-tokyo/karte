import logging


def init_logger():
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger("karte")
    logger.propagate = False

    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s : %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger(logger_name: str):
    logger = logging.getLogger(logger_name)
    logger.propagate = False
    return logger
