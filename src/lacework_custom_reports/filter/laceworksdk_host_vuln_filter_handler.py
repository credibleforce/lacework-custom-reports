from __future__ import print_function

from .filter_handler import filter_handler
import logging
from datetime import datetime
import pandas as pd
import json
import os

module_path = os.path.abspath(os.path.dirname(__file__))


class laceworksdk_host_vuln_filter_handler(filter_handler):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def filter(
                self,
                data,
                dataset=None,
                datasets=None
               ):

        # set report time
        report_start_time = datetime.strptime(dataset.get('start_time'), '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M')
        report_end_time = datetime.strptime(dataset.get('end_time'), '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M')

        # convert to dataframe before passing to filter
        df = pd.DataFrame(data)
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
        df = df.loc[
                (df['assessment_date'] >= report_start_time)
                & (df['assessment_date'] <= report_end_time)
            ]
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
        status = df[['assessment_day', 'cve_id', 'severity', 'status', 'fixed_time']].drop_duplicates(
                        subset=['assessment_day', 'cve_id', 'severity', 'status'], keep='last'
                    )

        latest_status = status.loc[status['assessment_day'] >= status['assessment_day'].max()]

        # count of fixed within reporting window
        total_fixed = len(status.loc[
                (status['status'] == 'Fixed')
                & (status['fixed_time'] >= report_start_time)
                & (status['fixed_time'] <= report_end_time)
            ].index)

        # total active count in last assessment
        total_active = int(latest_status.loc[
                (status['status'] == 'Active')
                | (status['status'] == 'Reopened')
            ].drop_duplicates(
                subset=['cve_id'], keep='last'
            )['cve_id'].count())

        # total new within reporting window
        total_new = len(df.loc[
                (df['status'] == 'New')
            ].drop_duplicates(
                subset=['cve_id'], keep='last'
            ).index)

        # status summary
        status_summary = status.groupby([
            'assessment_day',
            'cve_id',
            'severity',
            'status'
        ], as_index=False).size().rename(columns={"size": "count"})

        vuln_summary = status.loc[
                        (df['status'] == 'Active')
                        | (df['status'] == 'Reopened')
                    ].groupby([
                        'assessment_day',
                        'severity',
                    ], as_index=False).size().rename(columns={"size": "count"})

        # data summary
        data_summary = {
            "total_fixed": total_fixed,
            "total_active": total_active,
            "total_new": total_new,
            "severities": df['severity'].unique().tolist(),
            "assessment_dates": df['assessment_day'].unique().tolist(),
            "status_summary": json.loads(status_summary.to_json(date_format='iso')),
            "vuln_summary": json.loads(vuln_summary.to_json(date_format='iso')),
            "mttr": mttr,
            "mttr_days": mttr_days,
            "rows": len(df.index)
        }

        # convert to from dataframe
        json_data = json.loads(df.to_json(date_format='iso'))

        return json_data, data_summary
