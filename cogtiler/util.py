import os
import json
import logging
import logging.config


def configure_logging():
    """ Configure the logger """
    logging_config = os.path.join(os.path.dirname(__file__), 'logging.json')
    if os.path.exists(logging_config):
        with open(logging_config, encoding="utf-8") as config_file:
            config = json.load(config_file)
        logging.config.dictConfig(config)