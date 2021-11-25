#!/usr/bin/env python3

from __future__ import print_function

import os
import argparse
import json
import jinja2
import subprocess
from pyfiglet import Figlet

class HandlerConfig():
    def __init__(self,dataHandlersPath="./config/datatypes.json",reportHandlersPath="./config/reporttypes.json"):
        self.dataHandlersPath = dataHandlersPath
        self.reportHandlersPath = reportHandlersPath    
        self.dataHandlers = {}
        self.reportHandlers = {}
        self.load()

    def load(self):
        with open(self.dataHandlersPath) as f:
            self.dataHandlers = json.load(f)

        with open(self.reportHandlersPath) as f:
            self.reportHandlers = json.load(f)

    def dataHandlers(self):
        return self.dataHandlers

    def reportHandlers(self):
        return self.reportHandlers

class DataSetHandler():
    def __init__(self,dataset):
        self.dataset = dataset
        self.data = { "name": None, "data": None }
        self.load()
        self.generate()

    def load(self):
        return None

    def generate(self):
        return self.data
    
class LocalFileDataSetHandler(DataSetHandler):
    def load(self):
        with open(self.dataset['path']) as f:
            j = json.load(f)

        self.data = {
            "name": self.dataset['name'],
            "data": j
        }

class LaceworkCLIDataSetHandler(DataSetHandler):
    def load(self):
        command = 'lacework {0} {1} --json'.format(self.dataset['command'],self.dataset['args'])
        result = json.loads(subprocess.run(command, capture_output=True, text=True, shell=True).stdout)
        self.data = {
            "name": self.dataset['name'],
            "data": result
        }

class ReportHandler():
    def __init__(self,datasets,template,report):
        self.datasets = datasets
        loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(template))
        env = jinja2.Environment(loader=loader)
        self.template = env.get_template(os.path.basename(template))
        self.report = report

    def generate(self):
        pass

class LocalFileReportHandler(ReportHandler):
    def generate(self):
        with open(self.report['path'], 'w') as f:
            f.write(self.template.render(items=self.datasets))


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
    parser.add_argument('--config', required=True, help='path to config file')
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)
        for r in config['reports']:
            j = JustEffectivelyFormatting(report=r)  


if __name__ == '__main__':
    main()