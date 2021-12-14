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
            results = self.filterClass.filter(result.get('data'))
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
        last_report = df['assessment_date'].max()
        # all marked active as of latest assessment
        active = df.loc[(df['status'] == 'Active') & (df['assessment_date'] == last_report)]
        # all with first_seen_time in the reporting period as of latest assessment
        new = df.loc[(df['assessment_date'] == last_report) & (df['first_seen_time'] <= self.dataset.get('end_time')) & (df['first_seen_time'] >= self.dataset.get('start_time'))]
        # all with fixed_time in the reporting period as of latest assessment
        fixed = df.loc[(df['assessment_date'] == last_report) & (df['status'] == 'Fixed') & (df['fixed_time'] <= self.dataset.get('end_time')) & (df['fixed_time'] >= self.dataset.get('start_time'))]
        # all fixed both in an out of the reporting period
        all_fixed = df.loc[(df['status'] == 'Fixed') & (df['assessment_date'] == last_report)]

        severity_summary = df.loc[(df['status'] == 'Active')].set_index('assessment_date').groupby([pd.Grouper(freq='d'), 'severity'], as_index=False).size().rename(columns={"size": "count"})
        status_summary = df.set_index('assessment_date').groupby([pd.Grouper(freq='d'), 'severity', 'status'], as_index=False).size().rename(columns={"size": "count"})
        
        # total for the report period
        total_fixed = len(fixed.index)
        total_new = len(new.index)
        total_active = len(active.index)

        total_critical_fixed = len(fixed.loc[(df['severity']=='Critical')].index)
        total_critical_new = len(new.loc[(df['severity']=='Critical')].index)
        total_critical_active = len(active.loc[(df['severity']=='Critical')].index)

        total_high_fixed = len(fixed.loc[(df['severity']=='High')].index)
        total_high_new = len(new.loc[(df['severity']=='High')].index)
        total_high_active = len(active.loc[(df['severity']=='High')].index)

        total_medium_fixed = len(fixed.loc[(df['severity']=='Medium')].index)
        total_medium_new = len(new.loc[(df['severity']=='Medium')].index)
        total_medium_active = len(active.loc[(df['severity']=='Medium')].index)

        total_low_fixed = len(fixed.loc[(df['severity']=='Low')].index)
        total_low_new = len(new.loc[(df['severity']=='Low')].index)
        total_low_active = len(active.loc[(df['severity']=='Low')].index)

        total_info_fixed = len(fixed.loc[(df['severity']=='Info')].index)
        total_info_new = len(new.loc[(df['severity']=='Info')].index)
        total_info_active = len(active.loc[(df['severity']=='Info')].index)


        mttr = fixed['time_to_resolve'].mean()
        max_resolution_time = fixed['time_to_resolve'].max()
        min_resolution_time = fixed['time_to_resolve'].min()

        mttr_critical = fixed.loc[(df['severity']=='Critical')]['time_to_resolve'].mean()
        max_critical_resolution_time = fixed.loc[(df['severity']=='Critical')]['time_to_resolve'].max()
        min_critical_resolution_time = fixed.loc[(df['severity']=='Critical')]['time_to_resolve'].min()

        mttr_high = fixed.loc[(df['severity']=='High')]['time_to_resolve'].mean()
        max_high_resolution_time = fixed.loc[(df['severity']=='High')]['time_to_resolve'].max()
        min_high_resolution_time = fixed.loc[(df['severity']=='High')]['time_to_resolve'].min()

        mttr_medium = fixed.loc[(df['severity']=='Medium')]['time_to_resolve'].mean()
        max_medium_resolution_time = fixed.loc[(df['severity']=='Medium')]['time_to_resolve'].max()
        min_medium_resolution_time = fixed.loc[(df['severity']=='Medium')]['time_to_resolve'].min()

        mttr_low = fixed.loc[(df['severity']=='Low')]['time_to_resolve'].mean()
        max_low_resolution_time = fixed.loc[(df['severity']=='Low')]['time_to_resolve'].max()
        min_low_resolution_time = fixed.loc[(df['severity']=='Low')]['time_to_resolve'].min()

        mttr_info = fixed.loc[(df['severity']=='Info')]['time_to_resolve'].mean()
        max_info_resolution_time = fixed.loc[(df['severity']=='Info')]['time_to_resolve'].max()
        min_info_resolution_time = fixed.loc[(df['severity']=='Info')]['time_to_resolve'].min()
        
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
                "total_critical_fixed": total_critical_fixed,
                "total_critical_new": total_critical_new,
                "total_critical_active": total_critical_active,
                "total_high_fixed": total_high_fixed,
                "total_high_new": total_high_new,
                "total_high_active": total_high_active,
                "total_medium_fixed": total_medium_fixed,
                "total_medium_new": total_medium_new,
                "total_medium_active": total_medium_active,
                "total_low_fixed": total_low_fixed,
                "total_low_new": total_low_new,
                "total_low_active": total_low_active,
                "total_info_fixed": total_info_fixed,
                "total_info_new": total_info_new,
                "total_info_active": total_info_active,
                "mttr": mttr if not pd.isna(mttr) else 0,
                "mttr_days": round(mttr/1440) if not pd.isna(mttr) else 0,
                "max_resolution_time": max_resolution_time,
                "min_resolution_time": min_resolution_time,
                "mttr_critical": mttr_critical if not pd.isna(mttr_critical) else 0,
                "mttr_critical_days": round(mttr_critical/1440) if not pd.isna(mttr_critical) else 0,
                "max_critical_resolution_time": max_critical_resolution_time,
                "min_critical_resolution_time": min_critical_resolution_time,
                "mttr_high": mttr if not pd.isna(mttr_high) else 0,
                "mttr_high_days": round(mttr_high/1440) if not pd.isna(mttr_high) else 0,
                "max_high_resolution_time": max_high_resolution_time,
                "min_high_resolution_time": min_high_resolution_time,
                "mttr_medium": mttr_medium if not pd.isna(mttr_medium) else 0,
                "mttr_medium_days": round(mttr_medium/1440) if not pd.isna(mttr_medium) else 0,
                "max_medium_resolution_time": max_medium_resolution_time,
                "min_medium_resolution_time": min_medium_resolution_time,
                "mttr_low": mttr_low if not pd.isna(mttr_low) else 0,
                "mttr_low_days": round(mttr_low/1440) if not pd.isna(mttr_low) else 0,
                "max_low_resolution_time": max_low_resolution_time,
                "min_low_resolution_time": min_low_resolution_time,
                "mttr_info": mttr_info if not pd.isna(mttr_info) else 0,
                "mttr_info_days": round(mttr_info/1440) if not pd.isna(mttr_info) else 0,
                "max_info_resolution_time": max_info_resolution_time,
                "min_info_resolution_time": min_info_resolution_time,
                "mttr_all": mttr_all if not pd.isna(mttr_all) else 0,
                "mttr_all_days": round(mttr_all/1440) if not pd.isna(mttr_all) else 0,
                "max_resolution_time_all": max_resolution_time_all,
                "min_resolution_time_all": min_resolution_time_all
            }
        }