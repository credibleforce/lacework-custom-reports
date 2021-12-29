from __future__ import print_function

import os
import logging
import importlib

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
            module = importlib.import_module('.dataset.{0}'.format(d['type']), package="lacework_custom_reports")
            dataClass = getattr(module, d['type'])

            # enumerate the filter handlers and dynamically instanciate the class
            if d.get('filter') is not None:
                module = importlib.import_module('.filter.{0}'.format(d['filter']), package="lacework_custom_reports")
                filterClass = getattr(module, d['filter'])
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
            module = importlib.import_module('.report.{0}'.format(r['type']), package="lacework_custom_reports")
            reportClass = getattr(module, r['type'])

            reportClass(
                datasets=self.datasets,
                settings=self.settings,
                report=r).generate()
