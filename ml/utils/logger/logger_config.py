from logging import FileHandler, Logger, StreamHandler, getLogger

import coloredlogs


def get_logger(name: str) -> Logger:
    logger = getLogger(name)
    fmt = "%(asctime)s %(name)s %(levelname)s: %(message)s"
    coloredlogs.DEFAULT_FIELD_STYLES = {
        "asctime": {"color": "blue"},
        "name": {"color": "green"},
        "levelname": {"color": "yellow"},
    }
    coloredlogs.DEFAULT_LEVEL_STYLES["warning"] = {"color": 208}  # 208 is orange.
    handler = StreamHandler()

    handler.setFormatter(coloredlogs.ColoredFormatter(fmt))
    # Add the handler to the logger
    logger.addHandler(handler)
    coloredlogs.install(level="INFO", logger=logger)
    return logger


def get_response_logger(name: str) -> Logger:
    logger = getLogger(name)
    fmt = "%(message)s"

    handler = FileHandler("/var/logs/bid_response.log")
    handler.setFormatter(coloredlogs.ColoredFormatter(fmt))
    # Add the handler to the logger
    logger.addHandler(handler)
    logger.setLevel("INFO")
    return logger
