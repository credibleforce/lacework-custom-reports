from plugins.dataset.DataSetHandler import DataSetHandler
import json

class LocalFileDataSetHandler(DataSetHandler):
    def load(self):
        with open(self.dataset['path']) as f:
            j = json.load(f)

        self.data = {
            "name": self.dataset['name'],
            "data": j
        }