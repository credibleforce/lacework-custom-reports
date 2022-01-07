from __future__ import print_function

from .filter_handler import filter_handler
import logging
import pandas as pd
import json
import os

module_path = os.path.abspath(os.path.dirname(__file__))


class laceworkcli_s3_connections_filter_handler(filter_handler):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def filter(
                self,
                data,
                dataset=None,
                datasets=None
               ):
        # check to see if we were passed a dataframe
        if data is not pd.DataFrame:
            df = pd.DataFrame(data)
        else:
            df = data

        self.logger.info(df.head(1))

        # data summary
        data_summary = {
            "rows": len(df.index)
        }

        # convert to from dataframe
        json_data = json.loads(df.to_json(date_format='iso'))

        return json_data, data_summary
