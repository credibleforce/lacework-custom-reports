from __future__ import print_function

import jinja2
import os
import logging

module_path = os.path.abspath(os.path.dirname(__file__))

class report_handler():
    def __init__(self,datasets,settings,report):
        self.logger = logging.getLogger(__name__)
        self.datasets = datasets
        self.settings = settings
        self.report = report
        self.template = None
        self.parse_template()

    def parse_template(self):
        # allow report override for global template
        if 'template' in self.report.keys():
            loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(self.report['template']))
            env = jinja2.Environment(loader=loader,extensions=['jinja2.ext.do'])
            self.template = env.get_template(os.path.basename(self.report['template']))
        elif 'template' in self.settings.keys():
            loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(self.settings['template']))
            env = jinja2.Environment(loader=loader,extensions=['jinja2.ext.do'])
            self.template = env.get_template(os.path.basename(self.settings['template']))

    def generate(self):
        pass