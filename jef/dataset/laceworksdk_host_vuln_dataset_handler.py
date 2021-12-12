from __future__ import print_function

from .dataset_handler import dataset_handler
import json
import os

from datetime import datetime
from datetime import datetime, timedelta, timezone
from laceworksdk import LaceworkClient
import pandas as pd

module_path = os.path.abspath(os.path.dirname(__file__))

class laceworksdk_host_vuln_dataset_handler(dataset_handler):
    def load(self):
        
        lw = LaceworkClient(account=self.dataset.get('account'),
                    api_key=self.dataset.get('api_key'),
                    api_secret=self.dataset.get('api_secret'))
        
        # Build start/end times
        start_time = self.dataset.get('start_time')
        end_time = self.dataset.get('end_time')

        # build an array of days to compare daily results
        delta = datetime.strptime(end_time,'%Y-%m-%dT%H:%M:%SZ') - datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%SZ')  # returns timedelta
        days = []
        for i in range(delta.days + 1):
            day = datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%SZ') + timedelta(days=i)
            days.append(day.strftime('%Y-%m-%dT%H:%M:%SZ'))

        # set severity
        severity = self.dataset.get('severity')

        # set fixable
        fixable = self.dataset.get('fixable')

        # get vulns
        result = {
            'data': []
        }
        
        # get one report per day (good for comparing diffs over time)
        if self.dataset.get('time_day_split',False):
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
        
        # pass through a filter for parsing/manipulation if required
        if self.filterClass != None:
            results = self.filterClass.filter(result.get('data'))
        else:
            results = result.get('data')
        
        df = pd.DataFrame(results)
        rows = len(df.index)
        df['assessment_date']= pd.to_datetime(df['assessment_date'])

        severity_summary = df.set_index('assessment_date').groupby([pd.Grouper(freq='d'), 'severity']).size()
        status_summary = df.set_index('assessment_date').groupby([pd.Grouper(freq='d'), 'status']).size()

        json_data = json.loads(df.to_json(date_format='iso'))
        json_severity_summary = json.loads(severity_summary.to_json(date_format='iso'))
        json_status_summary = json.loads(status_summary.to_json(date_format='iso'))

        self.data = {
            "name": self.dataset.get('name'),
            "data": json_data,
            "summary": {
                "rows": rows,
                "severity": json_severity_summary,
                "status": json_status_summary
            }
        }