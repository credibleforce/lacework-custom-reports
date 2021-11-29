from __future__ import print_function

from .report_handler import report_handler
import os

module_path = os.path.abspath(os.path.dirname(__file__))

class s3_report_handler():
    def __init__(self):
        pass