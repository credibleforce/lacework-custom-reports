from __future__ import print_function

from lacework_custom_reports import dataset_handler
import json
import os

module_path = os.path.abspath(os.path.dirname(__file__))


class example_data_handler(dataset_handler):
    """
    Example data handler plugin. Override the load function with the dataset collection action.


    self.datasets = Contains any already generate datasets. Each dataset collection in execute in series.
    self.dataset = Contains settings for the current dataset taken from the config.
    self.data = Used to store the resultant data set in the format { "name": <datasetname>, "data": <json data> }

    """
    def load(self):
        result = json.loads({"example": "dataset"})
        self.data = {
            "name": self.dataset.get('name'),
            "data": result
        }
