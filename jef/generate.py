from __future__ import print_function

from .dataset.local_dataset_handler import local_dataset_handler
from .dataset.laceworkcli_dataset_handler import laceworkcli_dataset_handler
from .dataset.s3_dataset_handler import s3_dataset_handler
from .report.local_report_handler import local_report_handler
from .report.slack_report_handler import slack_report_handler
import os
import logging

module_path = os.path.abspath(os.path.dirname(__file__))

class generate():
    # init method or constructor   
    def __init__(self, report,plugins=[]):
        self.logger = logging.getLogger(__name__)
        self.datasource = report['datasources']
        self.reports = report['reports']
        self.settings = report['settings']
        self.datasets = {}
        self.outputs = []

        self.load()
        self.generate()

    def load(self):
        for d in self.datasource:
            
            # enumerate the data handlers and dynamically instanciate the class
            dataClass = globals()[d['type']]
            # provide the existing datasets for others to reference
            self.datasets[d['name']] = dataClass(d,self.datasets).generate()
            break
    
    def generate(self):
        for r in self.reports:
            # enumerate the report handlers and dynamically instanciate the class
            reportClass = globals()[r['type']]
            reportClass(datasets=self.datasets,settings=self.settings,report=r).generate()
            break