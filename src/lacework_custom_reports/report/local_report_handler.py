from __future__ import print_function

from .report_handler import report_handler
from datetime import datetime, timedelta
import os

module_path = os.path.abspath(os.path.dirname(__file__))


class local_report_handler(report_handler):
    def generate(self):
        with open(self.report.get('path'), 'w') as f:
            f.write(self.template.render(items=self.datasets,
                    date=datetime.utcnow(),
                    delta1d=timedelta(days=1),
                    delta1h=timedelta(hours=1),
                    delta30d=timedelta(days=30)))
