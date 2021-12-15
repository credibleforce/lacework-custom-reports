from __future__ import print_function

from .filter_handler import filter_handler
import logging
from datetime import datetime, timedelta
import pandas as pd
import json
import os

module_path = os.path.abspath(os.path.dirname(__file__))

class laceworkcli_s3_compliance_filter_handler(filter_handler):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def filter(self,df):
        results = []
        for index, row in df.iterrows():
            self.logger.info(row)
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
        
        df['reportTime'] = pd.to_datetime(df['reportTime'])

        status_summary = df.set_index('reportTime').groupby([pd.Grouper(freq='d'), 'num_compliant'], as_index=False).size().rename(columns={"size": "count"})
        
        return status_summary