from __future__ import print_function

from .filter_handler import filter_handler
import logging
import os

module_path = os.path.abspath(os.path.dirname(__file__))


class laceworkcli_s3_connections_filter_handler(filter_handler):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def filter(self, data, datasets=[]):
        self.logger.info(data.head(1))
        return data
