from __future__ import print_function

from .dataset_handler import dataset_handler
import json
import os

from datetime import datetime
from datetime import datetime, timedelta, timezone
from laceworksdk import LaceworkClient
import pandas as pd
import numpy as np

module_path = os.path.abspath(os.path.dirname(__file__))

class laceworksdk_host_vuln_dataset_handler(dataset_handler):
    def load(self):
        ###################################################################################################
        # Example sdk dataset handler - generally each function (e.g. vulnerability, compliance) will 
        # likely need it's own handler
        #
        # Data flow:
        # gather data > apply filter to format data set > use self.data to hold the result
        ###################################################################################################

        lw = LaceworkClient(account=self.dataset.get('account'),
                    api_key=self.dataset.get('api_key'),
                    api_secret=self.dataset.get('api_secret'))
        
        # Build start/end times
        start_time = datetime.strptime(self.dataset.get('start_time'),'%Y-%m-%dT%H:%M:%SZ')
        end_time = datetime.strptime(self.dataset.get('end_time'),'%Y-%m-%dT%H:%M:%SZ')

        # set severity
        severity = self.dataset.get('severity')

        # set fixable
        fixable = self.dataset.get('fixable')

        # data container
        result = {
            'data': []
        }

        # get one report per day (good for comparing diffs over time)
        if self.dataset.get('time_day_split',False):
            # build an array of days to compare daily results
            delta = end_time - start_time # returns timedelta
            days = []
            for i in range(delta.days + 1):
                day = start_time + timedelta(days=i)
                days.append(day.strftime('%Y-%m-%dT%H:%M:%SZ'))
                
            for i in range(len(days)-1):
                r = lw.vulnerabilities.get_host_vulnerabilities(start_time=days[i],end_time=days[i+1],severity=severity,fixable=fixable)
                
                if r.get('ok') != True:
                    self.logger.error("sdk call failed: {0}".format(r.get('message')))
                else:
                    result['data'] = result['data'] + r.get('data')
        # submit time range a return api handled time frame
        else:
            r = lw.vulnerabilities.get_host_vulnerabilities(start_time=days[i],end_time=days[i+1],severity=severity,fixable=fixable)

            if r.get('ok') != True:
                self.logger.error("sdk call failed: {0}".format(r.get('message')))
            else:
                result['data'] = result['data'] + r.get('data')
        
        # conver to dataframe before passing to filter
        df = pd.DataFrame(result.get('data'))

        # pass through a filter for parsing/manipulation if required
        if self.filterClass != None:
            df = self.filterClass().filter(df, self.datasets)
        
        rows = len(df.index)
        
        # convert to json
        json_data = json.loads(df.to_json(date_format='iso'))

        self.data = {
            "name": self.dataset.get('name'),
            "data": json_data,
            "summary": {
                "report_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "end_time": end_time.strftime('%Y-%m-%dT%H:%M:%SZ'), 
                "rows": rows
            }
        }