import logging
import colorlog

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:  # prevent duplicate handlers
        # Console handler
        stream_handler = colorlog.StreamHandler()
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(filename)s - %(levelname)s: %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        stream_handler.setFormatter(formatter)

        # File handler
        file_handler = logging.FileHandler("app.log", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(filename)s - %(levelname)s: %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
        ))

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger