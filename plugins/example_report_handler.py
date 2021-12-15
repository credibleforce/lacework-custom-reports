from __future__ import print_function

from jef.report.report_handler import report_handler
from datetime import datetime
import os

module_path = os.path.abspath(os.path.dirname(__file__))

class example_report_handler(report_handler):
    """
    Example report handler plugin. Override the generate function with the report action.

    
    self.datasets = Contains the resultant names datasets from the dataset handler
    self.settings = Contains the settings for the report
    self.report = Contains the report settings (e.g. template, name)

    """
    def generate(self):
        with open(self.report.get('path'), 'w') as f:
            f.write(self.template.render(items=self.datasets,date=datetime.utcnow()))