from __future__ import print_function

import os
import logging

module_path = os.path.abspath(os.path.dirname(__file__))

class dataset_handler():
    def __init__(self,dataset,datasets,filterClass=None):
        self.logger = logging.getLogger(__name__)
        
        # make previously build datasets accessible
        self.datasets = datasets

        # current dataset
        self.dataset = dataset
        
        # result object
        self.data = { "name": None, "data": None }

        # filter handler (optional)
        self.filterClass = filterClass

        # retrieve the dataset
        self.load()

        # return the resultant dataset
        self.generate()

    def load(self):
        """
        Overriden by specific data handlers, 
        pass a data filter class to manipulate 
        the data if required

        Returns:
            None: Nothing returned
        """
        return None

    def generate(self):
        """
        Used to return the parsed dataset

        Returns:
            json: the resultant json dataset
        """
        return self.data