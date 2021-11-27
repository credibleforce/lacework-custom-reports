from plugins.dataset.DataSetHandler import DataSetHandler
import json
import boto3
import gzip
import awswrangler as wr
import pytz
from datetime import datetime
from dateutil.parser import isoparse

class AWSS3DataHandler(DataSetHandler):
    def read_compressed_json(self, decompress):
        if decompress:
            with gzip.GzipFile(fileobj=object['Body']) as gzipfile:
                data = gzipfile.read().decode("utf-8")
        else:
            data = object['Body'].read().decode('utf-8')
        
        return data

    def parse_json(self,newline_separated,data):
        result = []
        if newline_separated:
            result = result + [json.loads(str(item)) for item in data.strip().split('\n')]
        else:
            result = result + [json.loads(data)]
        return result

    def load(self):
        s3_path = (self.dataset['s3_path'] if 's3_path' in self.dataset.keys() and self.dataset['s3_path'] else None)
        profile = (self.dataset['profile'] if 'profile' in self.dataset.keys() and self.dataset['profile'] else None)
        newline_separated = (self.dataset['newline_separated'] if 'newline_separated' in self.dataset.keys() and self.dataset['newline_separated'] else False)

        last_modified_begin = (self.dataset['last_modified_begin'] if 'last_modified_begin' in self.dataset.keys() and self.dataset['last_modified_begin'] else None)
        last_modified_end = (self.dataset['last_modified_end'] if 'last_modified_end' in self.dataset.keys() and self.dataset['last_modified_end'] else None)

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
        result = []
        if last_modified_filter:
            objects = wr.s3.list_objects(path=s3_path,last_modified_begin=begin_utc, last_modified_end=end_utc,boto3_session=s)
        else:
            objects = wr.s3.list_objects(path=s3_path,boto3_session=s)
            
        print(objects)
        print("Found: {0} files".format(len(objects)))
        for o in objects:
            result = result + [json.loads(wr.s3.read_json(o,lines=newline_separated,boto3_session=s).to_json())]
        
        self.data = {
            "name": self.dataset['name'],
            "data": result
        }