import logging
import sys
import os

DEFAULT_FORMATTER = 1
LOGGER_NAME_FORMATTER = 2
BASHLOG_FORMATTER=3

def setup_custom_logger(logger_name, log_file_path=None, formatter=DEFAULT_FORMATTER, log_level=logging.INFO, stream=sys.stdout):
    # Create a custom logger
    logger = logging.getLogger(logger_name)

    # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(log_level)

    if formatter == DEFAULT_FORMATTER:
        fmt = logging.Formatter(
            '[%(levelname)s] %(asctime)s: %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S")
    elif formatter == LOGGER_NAME_FORMATTER:
        fmt = logging.Formatter(
            '[%(levelname)s] %(asctime)s - %(name)s: %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S")
    elif formatter == BASHLOG_FORMATTER:
        fmt = logging.Formatter(
            '%(asctime)s [%(levelname)s] - %(message)s',
            datefmt="%x %T")
    else:
        fmt = logging.Formatter(
            '[%(levelname)s] %(asctime)s: %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S")        

    # Create a stream handler and set the formatter
    stream_handler = logging.StreamHandler(stream)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    # Add the handlers to the logger
    if log_file_path:
        dirname = "/".join(log_file_path.split('/')[0:-1])
        try:
            os.makedirs(dirname)
        except FileExistsError:
            pass

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
        
    return logger