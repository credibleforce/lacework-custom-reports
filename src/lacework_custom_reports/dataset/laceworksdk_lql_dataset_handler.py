from __future__ import print_function

from .dataset_handler import dataset_handler
import os

from datetime import datetime
from laceworksdk import LaceworkClient
import pandas as pd
import json

module_path = os.path.abspath(os.path.dirname(__file__))

INTERVAL = 1200
PAGINATION_MAX = 5000
WORKER_THREADS = 10


class laceworksdk_lql_dataset_handler(dataset_handler):
    def load(self):
        self.lw_client = LaceworkClient(account=self.dataset.get('account'),
                                        api_key=self.dataset.get('api_key'),
                                        api_secret=self.dataset.get('api_secret'))

        # Get LQL Query
        query_text = self.dataset.get('query_text')
        self.logger.info(query_text)
        # Build start/end times
        start_time = datetime.strptime(self.dataset.get('start_time'), '%Y-%m-%dT%H:%M:%SZ')
        end_time = datetime.strptime(self.dataset.get('end_time'), '%Y-%m-%dT%H:%M:%SZ')

        # Query for active containers across registries
        response = self.lw_client.queries.execute(
            evaluator_id='<<IMPLICIT>>',
            query_text=query_text,
            arguments={
                'StartTimeRange': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'EndTimeRange': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            }
        )

        result = response.get('data', [])

        num_returned = len(result)
        if num_returned == PAGINATION_MAX:
            self.logger.warning(f'Warning! The maximum number of active containers ({PAGINATION_MAX}) was returned.')

        # pass through a filter for parsing/manipulation if required
        if self.filterClass is not None:
            results = self.filterClass().filter(result)
        else:
            results = result

        df = pd.DataFrame(results)
        json_data = json.loads(df.to_json(date_format='iso'))

        self.data = {
            "name": self.dataset.get('name'),
            "data": json_data,
            "summary": {
                "rows": len(df.index)
            }
        }
        return None
