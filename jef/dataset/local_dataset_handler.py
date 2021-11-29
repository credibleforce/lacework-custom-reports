from __future__ import print_function

from .dataset_handler import dataset_handler
import json
import os

module_path = os.path.abspath(os.path.dirname(__file__))

class local_dataset_handler(dataset_handler):
    def load(self):
        with open(self.dataset['path']) as f:
            j = json.load(f)

        self.data = {
            "name": self.dataset['name'],
            "data": j
        }