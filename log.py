from colorama import init, Fore, Style
import logging

init()


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        reset = Style.RESET_ALL if color else ""
        return f"{color}{super().format(record)}{reset}"


def init_logger():
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger("karte")
    logger.propagate = False

    handler = logging.StreamHandler()

    formatter = ColorFormatter("%(asctime)s - %(levelname)s - %(name)s : %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger(logger_name: str):
    logger = logging.getLogger(logger_name)
    logger.propagate = False
    return logger
