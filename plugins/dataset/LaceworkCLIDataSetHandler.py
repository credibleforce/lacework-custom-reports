from plugins.dataset.DataSetHandler import DataSetHandler
import json
import subprocess

class LaceworkCLIDataSetHandler(DataSetHandler):
    def load(self):
        command = 'lacework {0} {1} --json'.format(self.dataset['command'],self.dataset['args'])
        result = json.loads(subprocess.run(command, capture_output=True, text=True, shell=True).stdout)
        self.data = {
            "name": self.dataset['name'],
            "data": result
        }