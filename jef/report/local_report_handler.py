from __future__ import print_function

from .report_handler import report_handler
import os

module_path = os.path.abspath(os.path.dirname(__file__))

class local_report_handler(report_handler):
    def generate(self):
        with open(self.report['path'], 'w') as f:
            f.write(self.template.render(items=self.datasets))