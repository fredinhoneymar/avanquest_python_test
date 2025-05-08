import logging
import os

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers if the logger is already configured
    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter('%(message)s')

    # Directory where logs will be saved
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True) 

    log_file = os.path.join(log_dir, 'pipeline.log')

    # File handler for log file
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # Handler to display logs in the terminal
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
