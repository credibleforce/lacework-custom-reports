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
        # Vulnerability report
        #
        # Data flow:
        # gather data > apply filter to format data set > use self.data to hold the result
        #
        # To do:
        # Ideally each of these handlers pass a standard data type (e.g. dataframe) to the filter class.
        # Currently this handler does not follow that pattern.
        #
        ###################################################################################################

        lw = LaceworkClient(account=self.dataset.get('account'),
                    api_key=self.dataset.get('api_key'),
                    api_secret=self.dataset.get('api_secret'))
        
        # Build start/end times
        start_time = datetime.strptime(self.dataset.get('start_time'),'%Y-%m-%dT%H:%M:%SZ')
        end_time = datetime.strptime(self.dataset.get('end_time'),'%Y-%m-%dT%H:%M:%SZ')

        # build an array of days to compare daily results
        delta = end_time - start_time # returns timedelta
        days = []
        for i in range(delta.days + 1):
            day = start_time + timedelta(days=i)
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
            results = self.filterClass().filter(result.get('data'))
        else:
            results = result.get('data')
        
        df = pd.DataFrame(results)
        rows = len(df.index)

        df['assessment_date'] = pd.to_datetime(df['assessment_date'])
        df['fixed_time'] = pd.to_datetime(df['fixed_time'])
        df['last_updated_time'] = pd.to_datetime(df['last_updated_time'])
        df['first_seen_time'] = pd.to_datetime(df['first_seen_time'])
        df['time_to_resolve'] = pd.to_numeric(df['time_to_resolve'])
        
        # build summary data - use most recent assessment date
        last_assessment = df['assessment_date'].max()
        last_report_start_time = (last_assessment - timedelta(days=1)).strftime('%Y-%m-%d')
        last_report_end_time = last_assessment.strftime('%Y-%m-%d')
        last_report = df.loc[(df['assessment_date']>=last_report_start_time) & (df['assessment_date']<=last_report_end_time)]

        # all marked active as of latest assessment
        active =  last_report.loc[(df['status'] == 'Active')]
        # all with first_seen_time in the reporting period as of latest assessment
        new = last_report.loc[(df['first_seen_time'] <= self.dataset.get('end_time')) & (df['first_seen_time'] >= self.dataset.get('start_time'))]
        # all with fixed_time in the reporting period as of latest assessment
        fixed = last_report.loc[(df['status'] == 'Fixed') & (df['fixed_time'] <= self.dataset.get('end_time')) & (df['fixed_time'] >= self.dataset.get('start_time'))]
        # all fixed both in an out of the reporting period
        all_fixed = last_report.loc[(df['status'] == 'Fixed')]

        severity_summary = df.loc[(df['status'] == 'Active')].set_index('assessment_date').groupby([pd.Grouper(freq='d'), 'severity'], as_index=False).size().rename(columns={"size": "count"})
        status_summary = df.set_index('assessment_date').groupby([pd.Grouper(freq='d'), 'severity', 'status'], as_index=False).size().rename(columns={"size": "count"})
        
        # total for the report period
        total_fixed = len(fixed.index)
        total_new = len(new.index)
        total_active = len(active.index)

        mttr = fixed['time_to_resolve'].mean()
        max_resolution_time = fixed['time_to_resolve'].max()
        min_resolution_time = fixed['time_to_resolve'].min()
        
        # totals including those fixed outside the report period
        mttr_all = all_fixed['time_to_resolve'].mean()
        max_resolution_time_all = all_fixed['time_to_resolve'].max()
        min_resolution_time_all = all_fixed['time_to_resolve'].min()
        
        # convert to json
        json_data = json.loads(df.to_json(date_format='iso'))
        json_severity_summary = json.loads(severity_summary.to_json(date_format='iso'))
        json_status_summary = json.loads(status_summary.to_json(date_format='iso'))

        self.data = {
            "name": self.dataset.get('name'),
            "data": json_data,
            "summary": {
                "report_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "end_time": end_time.strftime('%Y-%m-%dT%H:%M:%SZ'), 
                "rows": rows,
                "severity": json_severity_summary,
                "status": json_status_summary,
                "total_fixed": total_fixed,
                "total_new": total_new,
                "total_active": total_active,
                "mttr": mttr if not pd.isna(mttr) else 0,
                "mttr_days": round(mttr/1440) if not pd.isna(mttr) else 0,
                "max_resolution_time": max_resolution_time,
                "min_resolution_time": min_resolution_time,
                "mttr_all": mttr_all if not pd.isna(mttr_all) else 0,
                "mttr_all_days": round(mttr_all/1440) if not pd.isna(mttr_all) else 0,
                "max_resolution_time_all": max_resolution_time_all,
                "min_resolution_time_all": min_resolution_time_all
            }
        }