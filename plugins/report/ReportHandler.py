import jinja2
import os

class ReportHandler():
    def __init__(self,datasets,template,report):
        self.datasets = datasets
        if template != None:
            loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(template))
            env = jinja2.Environment(loader=loader)
            self.template = env.get_template(os.path.basename(template))
        else:
            self.template = None
        self.report = report

    def generate(self):
        pass