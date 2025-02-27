from __future__ import print_function

from .dataset_handler import dataset_handler
import json
import boto3
import gzip
import awswrangler as wr
import pytz
from datetime import datetime
from dateutil.parser import isoparse
import pandas as pd
import os

module_path = os.path.abspath(os.path.dirname(__file__))


class s3_dataset_handler(dataset_handler):
    def read_compressed_json(self, decompress):
        if decompress:
            with gzip.GzipFile(fileobj=object['Body']) as gzipfile:
                data = gzipfile.read().decode("utf-8")
        else:
            data = object['Body'].read().decode('utf-8')

        return data

    def parse_json(self, newline_separated, data):
        result = []
        if newline_separated:
            result = result + [json.loads(str(item)) for item in data.strip().split('\n')]
        else:
            result = result + [json.loads(data)]
        return result

    def load(self):
        # initialize result objects
        json_data = {}
        data_summary = {}

        s3_path = self.dataset.get('s3_path')
        profile = self.dataset.get('profile')
        newline_separated = self.dataset.get('newline_separated', False)

        last_modified_begin = self.dataset.get('last_modified_begin')
        last_modified_end = self.dataset.get('last_modified_end')

        self.logger.info("Loading s3 bucket: {0}".format(s3_path))

        last_modified_filter = False
        if last_modified_begin and last_modified_end:
            last_modified_filter = True
            begin = isoparse(last_modified_begin)
            end = isoparse(last_modified_end)

            begin_utc = pytz.utc.localize(begin)
            end_utc = pytz.utc.localize(end)

        if profile:
            s = boto3.session.Session(profile_name=profile)
        else:
            s = boto3.session.Session()

        # enumerate results
        dfs = []
        if last_modified_filter:
            objects = wr.s3.list_objects(
                path=s3_path,
                last_modified_begin=begin_utc,
                last_modified_end=end_utc,
                boto3_session=s)
        else:
            objects = wr.s3.list_objects(
                path=s3_path,
                boto3_session=s)

        self.logger.info("Found: {0} files".format(len(objects)))
        for o in objects:
            data = wr.s3.read_json(
                o,
                lines=newline_separated,
                boto3_session=s)
            dfs.append(data)

        # concat all results into single dataframe
        df = pd.concat(dfs, ignore_index=True)

        # pass through a filter for parsing/manipulation if required
        if self.filterClass is not None:
            json_data, data_summary = self.filterClass().filter(df, dataset=self.dataset, datasets=self.datasets)
        else:
            json_data = json.loads(df.to_json(date_format='iso'))
            data_summary = {
                "rows": len(df.index)
            }

        self.data = {
            "name": self.dataset['name'],
            "data": json_data,
            "summary": {
                "report_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "start_time": begin_utc.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "end_time": end_utc.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "rows": data_summary.get('rows'),
                "data_summary": data_summary
            }
        }
