from __future__ import print_function

from .report_handler import report_handler
import json
import boto3
import gzip
import awswrangler as wr
import pytz
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from urllib.parse import urlparse
import io
import os

module_path = os.path.abspath(os.path.dirname(__file__))

class s3_report_handler(report_handler):
    def gzip_content(self, input):
        with gzip.GzipFile(fileobj=object['Body']) as gzipfile:
            compressed = gzipfile.write(input)
        
        return compressed
    
    def generate(self):
        self.logger.debug("Loading s3 bucket...")
        s3_path = self.report.get('s3_path')
        profile = self.report.get('profile')
        compressed = self.report.get('compressed',False)
        
        # write newline for each item in array
        newline_separated = self.report.get('newline_separated',False)

        if profile:
            s = boto3.session.Session(profile_name=profile)
        else:
            s = boto3.session.Session()

        # write results
        data = self.template.render(items=self.datasets,date=datetime.utcnow(),delta1d=timedelta(days=1),delta1h=timedelta(hours=1),delta30d=timedelta(days=30)).encode('utf-8')
        
        if compressed:
            wr.s3.upload(local_file=io.BytesIO(gzip.compress(data)),path="{0}.gz".format(s3_path),boto3_session=s)
        else:
            wr.s3.upload(local_file=io.BytesIO(data),path=s3_path,boto3_session=s)
            