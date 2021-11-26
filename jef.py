#!/usr/bin/env python3

from __future__ import print_function

import argparse
import json
from plugins.config.HandlerConfig import HandlerConfig
from plugins.dataset.LocalFileDataSetHandler import LocalFileDataSetHandler
from plugins.dataset.LaceworkCLIDataSetHandler import LaceworkCLIDataSetHandler
from plugins.report.LocalFileReportHandler import LocalFileReportHandler
from plugins.report.SlackReportHandler import SlackReportHandler
from pyfiglet import Figlet


class JustEffectivelyFormatting():
    # init method or constructor   
    def __init__(self, report):
        handlerConfig = HandlerConfig()
        self.dataHandlers = handlerConfig.dataHandlers
        self.reportHandler = handlerConfig.reportHandlers
        self.datasource = report['datasources']
        self.reports = report['reports']
        self.template = report['template']
        self.datasets = {}
        self.outputs = []

        self.load()
        self.generate()

    def load(self):
        for d in self.datasource:
            # enumerate the data handlers and dynamically instanciate the class
            for t in self.dataHandlers.keys():
                if t == d['type']:
                    dataClass = globals()[self.dataHandlers[t]]
                    self.datasets[d['name']] = dataClass(d).generate()
                    break
    
    def generate(self):
        for r in self.reports:
            # enumerate the report handlers and dynamically instanciate the class
            for t in self.reportHandler.keys():
                if t == r['type']:
                    dataClass = globals()[self.reportHandler[t]]
                    dataClass(datasets=self.datasets,template=self.template,report=r).generate()
                    break

def main():
    ''' Parsing inputs '''
    ver = "0.0.1"
    dsc = "Just Effectively Formatting"

    print(Figlet(font="3-d").renderText("JEF"))
    print("{0} [{1}]\n".format(dsc,ver))

    parser = argparse.ArgumentParser(description=dsc)
    parser.add_argument('--reports', required=True, help='path to config file')
    args = parser.parse_args()

    with open(args.reports) as f:
        config = json.load(f)
        for r in config['reports']:
            j = JustEffectivelyFormatting(report=r)  


if __name__ == '__main__':
    main()