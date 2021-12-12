from __future__ import print_function

import os
import logging

module_path = os.path.abspath(os.path.dirname(__file__))

class filter_handler():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def filter(data):
        """
        Overriden by specific data handlers

        Returns:
            None: Nothing returned
        """
        return data