"""
Application for launching programs from a external media
device library by moving it to a local drive for speed.

Purpose:
Some programs are used occasionally or too large to be
installed on the local machine.

Compatibility:
- Steam Games
- Standalone Games
- Standalone Applications
"""
import os
import logging
import logging.handlers
import pathlib
import source

config_handler = source.config_handler.ConfigHandler()


def get_logger():
    """
    Returns a configured logger instance.
    If the logger is already configured, it simply returns the existing logger.
    """
    logger = logging.getLogger(__name__)
    if not logger.hasHandlers():  # Ensure the logger is configured only once
        config = config_handler.get_config()

        log_file = config["paths"]["logFile"]
        # check if the log file path is relative or absolute
        if not os.path.isabs(log_file):
            # Make the log file path absolute by joining it with the directory of the current script
            log_file = os.path.join(pathlib.Path(__file__).parent, log_file)
            # Ensure the directory exists
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                # Create the directory if it doesn't exist
                os.makedirs(log_dir)
                logger.debug("Created log directory: %s", log_dir)
            else:
                logger.debug("Log directory already exists: %s", log_dir)
        log_level = config["settings"]["logLevel"].upper()
        log_level = getattr(logging, log_level)

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        logger.debug("Logging configured with level: %s and log file: %s", log_level, log_file)

    return logger


def main():
    """
    Main function to run the CacheLauncher application.
    """
    logger = get_logger()
    config = config_handler.get_config()
    logger.info("Starting %s application.", config['appName'])

    print(f"""
            appName: {config['appName']}
            version: {config['version']}
            settings: {config['settings']}
            paths: {config['paths']}
    """)


if __name__ == "__main__":
    main()
