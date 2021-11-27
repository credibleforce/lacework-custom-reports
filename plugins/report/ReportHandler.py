import jinja2
import os

class ReportHandler():
    def __init__(self,datasets,settings,report):
        self.datasets = datasets
        self.settings = settings
        self.report = report
        self.template = None
        self.parse_template()

    def parse_template(self):
        if self.settings['template'] != None:
            loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(self.settings['template']))
            env = jinja2.Environment(loader=loader)
            self.template = env.get_template(os.path.basename(self.settings['template']))
        else:
            self.template = None

    def generate(self):
        pass