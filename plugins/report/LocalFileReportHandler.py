from plugins.report.ReportHandler import ReportHandler

class LocalFileReportHandler(ReportHandler):
    def generate(self):
        with open(self.report['path'], 'w') as f:
            f.write(self.template.render(items=self.datasets))