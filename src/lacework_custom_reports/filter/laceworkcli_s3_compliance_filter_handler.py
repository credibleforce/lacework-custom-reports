from __future__ import print_function

from .filter_handler import filter_handler
import logging
import pandas as pd
import json
import os

module_path = os.path.abspath(os.path.dirname(__file__))


class laceworkcli_s3_compliance_filter_handler(filter_handler):
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

        results = []
        for index, row in data.iterrows():
            result = {
                    "report_time": row['summary']['report_time'],
                    "rows": row['summary']['rows'],
                }

            for k in row['data']['summary'][0].keys():
                result[k] = row['data']['summary'][0][k]

            for k in row['data'].keys():
                if k not in ['summary', 'recommendations']:
                    result[k] = row['data'][k]

            results.append(result)

        df = pd.DataFrame(results)

        df['report_time'] = pd.to_datetime(df['report_time'], format='%Y-%m-%dT%H:%M:%SZ')
        df['reportTime'] = pd.to_datetime(df['reportTime'])

        df = df.set_index('report_time').groupby([pd.Grouper(freq='d')], as_index=True).sum().reset_index()
        self.logger.info(df)

        # data summary
        data_summary = {
            "rows": len(df.index)
        }

        # convert to from dataframe
        json_data = json.loads(df.to_json(date_format='iso'))

        return json_data, data_summary
