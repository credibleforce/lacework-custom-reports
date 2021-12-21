from __future__ import print_function

# dataset handler
from .dataset.local_dataset_handler import local_dataset_handler
from .dataset.laceworkcli_dataset_handler import laceworkcli_dataset_handler
from .dataset.laceworksdk_host_vuln_dataset_handler import laceworksdk_host_vuln_dataset_handler
from .dataset.s3_dataset_handler import s3_dataset_handler

# report handler
from .report.local_report_handler import local_report_handler
from .report.slack_report_handler import slack_report_handler
from .report.s3_report_handler import s3_report_handler

# filter handler
from .filter.laceworksdk_host_vuln_filter_handler import laceworksdk_host_vuln_filter_handler
from .filter.laceworkcli_s3_compliance_filter_handler import laceworkcli_s3_compliance_filter_handler
from .filter.laceworkcli_s3_connections_filter_handler import laceworkcli_s3_connections_filter_handler
from .filter.laceworkcli_s3_connections_summary_filter_handler import laceworkcli_s3_connections_summary_filter_handler
from .filter.laceworkcli_compliance_summary_filter_handler import laceworkcli_compliance_summary_filter_handler

import os
import logging

module_path = os.path.abspath(os.path.dirname(__file__))

class generate():
    # init method or constructor   
    def __init__(self, report,plugins=[]):
        self.logger = logging.getLogger(__name__)
        self.datasource = report.get('datasources')
        self.reports = report.get('reports')
        self.settings = report.get('settings')
        self.datasets = {}
        self.outputs = []

        self.load()
        self.generate()

    def load(self):
        for d in self.datasource:
            
            # enumerate the data handlers and dynamically instanciate the class
            dataClass = globals()[d['type']]
            
            # enumerate the filter handlers and dynamically instanciate the class
            if d.get('filter') != None:
                filterClass = globals()[d['filter']]
            else:
                filterClass = None

            # provide the existing datasets for others to reference
            self.datasets[d['name']] = dataClass(d,self.datasets,filterClass=filterClass).generate()
    
    def generate(self):
        for r in self.reports:
            # enumerate the report handlers and dynamically instanciate the class
            reportClass = globals()[r['type']]
            reportClass(datasets=self.datasets,settings=self.settings,report=r).generate()