from __future__ import print_function

from .dataset_handler import dataset_handler
import json
import pandas as pd
import os

module_path = os.path.abspath(os.path.dirname(__file__))


class local_dataset_handler(dataset_handler):
    def load(self):
        # initialize result objects
        json_data = {}
        data_summary = {}

        with open(self.dataset.get('path')) as f:
            json_data = json.load(f)

        # pass through a filter for parsing/manipulation if required
        if self.filterClass is not None:
            json_data, data_summary = self.filterClass().filter(json_data, dataset=self.dataset)
        else:
            json_data = json.loads(pd.DataFrame(json_data).to_json(date_format='iso'))
            data_summary = {
                "rows": len(json_data)
            }

        data_summary = {
            "rows": len(json_data)
        }

        self.data = {
            "name": self.dataset.get('name'),
            "data": json_data,
            "summary": {
                "rows": data_summary.get('rows'),
                "data_summary": data_summary
            }
        }
