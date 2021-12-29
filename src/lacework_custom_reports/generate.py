from __future__ import print_function

# dataset handler

# report handler

# filter handler

import os
import logging

module_path = os.path.abspath(os.path.dirname(__file__))


class generate():
    # init method or constructor
    def __init__(self, report, plugins=[]):
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
            if d.get('filter') is not None:
                filterClass = globals()[d['filter']]
            else:
                filterClass = None

            # provide the existing datasets for others to reference
            self.datasets[d['name']] = dataClass(
                d,
                self.datasets,
                filterClass=filterClass).generate()

    def generate(self):
        for r in self.reports:
            # enumerate the report handlers and dynamically instanciate the class
            reportClass = globals()[r['type']]
            reportClass(
                datasets=self.datasets,
                settings=self.settings,
                report=r).generate()
