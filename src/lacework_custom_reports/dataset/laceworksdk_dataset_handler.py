from __future__ import print_function

from .dataset_handler import dataset_handler
import json
import os

from datetime import datetime, timedelta
from laceworksdk import LaceworkClient
import pandas as pd
# import numpy as np

module_path = os.path.abspath(os.path.dirname(__file__))


class laceworksdk_dataset_handler(dataset_handler):

    def load(self):
        ###################################################################################################
        # Example sdk dataset handler - generally each function (e.g. vulnerability, compliance) will
        # likely need it's own handler
        #
        # Data flow:
        # gather data > apply filter to format data set > use self.data to hold the result
        ###################################################################################################

        self.lw = LaceworkClient(account=self.dataset.get('account'),
                                 subaccount=self.dataset.get('subaccount'),
                                 api_key=self.dataset.get('api_key'),
                                 api_secret=self.dataset.get('api_secret'),
                                 instance=self.dataset.get('instance'),
                                 base_domain=self.dataset.get('base_domain'),
                                 profile=self.dataset.get('profile')
                                 )

        # Build start/end times
        start_time = datetime.strptime(self.dataset.get('start_time'), '%Y-%m-%dT%H:%M:%SZ')
        end_time = datetime.strptime(self.dataset.get('end_time'), '%Y-%m-%dT%H:%M:%SZ')

        # set severity
        severity = self.dataset.get('severity')

        # set fixable
        fixable = self.dataset.get('fixable')

        # data container
        result = {
            'data': [],
            'summary': {}
        }

        # build an array of days to compare daily results
        days = []
        # returns timedelta
        delta = end_time - start_time

        for i in range(delta.days + 1):
            day = start_time + timedelta(days=i)
            days.append(day.strftime('%Y-%m-%dT%H:%M:%SZ'))

        # get one report per day (good for comparing diffs over time)
        if self.dataset.get('time_day_split', False):

            for i in range(len(days)-1):
                r = self.lw.vulnerabilities.get_host_vulnerabilities(
                    start_time=days[i],
                    end_time=days[i+1],
                    severity=severity,
                    fixable=fixable)

                if r.get('ok') is not True:
                    self.logger.error("sdk call failed: {0}".format(r.get('message')))
                else:
                    result['data'] = result['data'] + r.get('data')
        # submit time range a return api handled time frame
        else:
            r = self.lw.vulnerabilities.get_host_vulnerabilities(
                start_time=days[0],
                end_time=days[-1],
                severity=severity,
                fixable=fixable)

            if r.get('ok') is not True:
                self.logger.error("sdk call failed: {0}".format(r.get('message')))
            else:
                result['data'] = result['data'] + r.get('data')

        # conver to dataframe before passing to filter
        df = pd.DataFrame(result['data'])
        df.flags.allows_duplicate_labels = False
        df = df.explode('packages').reset_index(drop=True)
        df = df.join(pd.json_normalize(df.packages))
        df['severity'] = df['summary'].apply(lambda x: next(iter(x.get('severity'))))
        df['severity_detail'] = df['summary'].apply(lambda x: x.get('severity').get(next(iter(x.get('severity')))))
        df = df.join(pd.json_normalize(df['severity_detail']).add_prefix('severity_'))
        df['total_vulnerabilities'] = df['summary'].apply(lambda x: x.get('total_vulnerabilities'))
        df['last_evaluation_time'] = df['summary'].apply(lambda x: x.get('last_evaluation_time'))
        df['total_exception_vulnerabilities'] = df['summary'].apply(lambda x: x.get('total_exception_vulnerabilities'))
        df['assessment_date'] = pd.to_datetime(
                    df['last_evaluation_time'].apply(
                        lambda x: datetime.fromtimestamp(int(x)/1000)
                    ), utc=True
                )
        df['assessment_day'] = df['assessment_date'].dt.strftime('%Y-%m-%d')
        df['last_updated_time'] = pd.to_datetime(df['last_updated_time'], utc=True)
        df['first_seen_time'] = pd.to_datetime(df['first_seen_time'], utc=True)
        df['time_to_resolve'] = pd.to_numeric(df['time_to_resolve'])
        df['fixed_time'] = pd.to_datetime(df['first_seen_time'] + pd.to_timedelta(df['time_to_resolve'], unit='m'))

        # set index
        df.set_index(pd.DatetimeIndex(df['assessment_date']), drop=True, inplace=True)

        # sort data
        df.sort_values([
                "assessment_day",
                "cve_id", "name",
                "namespace",
                "status"
            ], ascending=(
                True,
                True,
                True,
                True,
                True
            ), inplace=True)

        # drop duplicates
        df.drop_duplicates(subset=[
                                    'assessment_day',
                                    'cve_id',
                                    'name',
                                    'namespace'
                        ], keep='last', inplace=True)

        # count packages per cve
        df['total_vulnerability_count'] = df.groupby([
                    'assessment_day',
                    'cve_id',
                    'status'
        ])['status'].transform('count')

        df.drop(columns=['packages', 'summary', 'last_evaluation_time', 'severity_detail'], inplace=True)
        df.reset_index(drop=True, inplace=True)

        mttr = df.loc[(df['status'] == 'Fixed')]['time_to_resolve'].mean()
        mttr_days = round(mttr/1440) if not pd.isna(mttr) else 0

        # build latest status by cve, name, namespace
        status = df.drop_duplicates(subset=['cve_id', 'name', 'namespace', 'status'], keep='last')

        # count of fixed within reporting window
        total_fixed = len(status.loc[
                (status['status'] == 'Fixed')
                & (status['fixed_time'] <= self.dataset.get('end_time'))
                & (status['fixed_time'] >= self.dataset.get('start_time'))
            ].index)

        # total active unique cve, name, namespace within reporting window
        total_active = len(status.loc[
                (status['status'] == 'Active')
                | (status['status'] == 'Reopened')
            ].index)

        # total new within reporting window
        total_new = len(df.loc[
                (df['status'] == 'New')
            ].index)

        # status summary
        status_summary = df.groupby([
                'assessment_day',
                'status',
                'severity'
            ], as_index=False).size().rename(columns={"size": "count"})

        # data summary
        data_summary = {
            "total_fixed": total_fixed,
            "total_active": total_active,
            "total_new": total_new,
            "severities": df['severity'].unique().tolist(),
            "assessment_dates": df['assessment_day'].unique().tolist(),
            "status_summary": json.loads(status_summary.to_json(date_format='iso')),
            "mttr": mttr,
            "mttr_days": mttr_days
        }

        # convert to from dataframe
        json_data = json.loads(df.to_json(date_format='iso'))

        self.data = {
            "name": self.dataset.get('name'),
            "data": json_data,
            "summary": {
                "report_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "end_time": end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "rows": len(df.index),
                "data_summary": data_summary
            }
        }
