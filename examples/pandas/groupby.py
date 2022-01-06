#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
import json

data = None
with open('data/dataset3.json') as f:
    data = json.load(f)

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
df['assessment_date'] = pd.to_datetime(df['last_evaluation_time'].apply(lambda x: datetime.fromtimestamp(int(x)/1000)))
df['last_updated_time'] = pd.to_datetime(df['last_updated_time'])
df['first_seen_time'] = pd.to_datetime(df['first_seen_time'])
df.drop(columns=['packages', 'summary', 'last_evaluation_time', 'severity_detail'], inplace=True)
df.set_index(df['assessment_date'], inplace=True)


# "time_to_resolve":"105840"

# last_updated_time = datetime.strptime(p.get('last_updated_time'), '%a, %d %b %Y %H:%M:%S %z')
# first_seen_time = datetime.strptime(p.get('first_seen_time'), '%a, %d %b %Y %H:%M:%S %z')

# last_updated_time = datetime.strptime(df.get('last_updated_time'), '%a, %d %b %Y %H:%M:%S %z')
# first_seen_time = datetime.strptime(df.get('first_seen_time'), '%a, %d %b %Y %H:%M:%S %z')

# if p.get('status') == 'Fixed':
#     fixed_time = (
#         first_seen_time + timedelta(minutes=int(df.get('time_to_resolve')))
#     ).strftime('%Y-%m-%dT%H:%M:%SZ')
# else:
#     fixed_time = None

# print(df.loc[df['cve_id'] == 'CVE-2021-43527'])
# print(df)
# print(test)
# assessment_date
# cve_id
# name
# namespace
# fix_available
# version
# fixed_version
# severity
# cve_link
# cvss_score
# status
# package_status
# last_updated_time
# first_seen_time
# time_to_resolve
# fixed_time
# exception_fixable
# exception_vulnerabilities
# fixable
# vulnerabilities
# total_vulnerabilities
# total_exception_vulnerabilities

# df = df.join(pd.json_normalize(df.summary))
# df.drop(columns=['summary'], inplace=True)
# print(df)
# df['assessment_date = datetime.fromtimestamp(int(d.get('summary').get('last_evaluation_time'))/1000)
# df.astype(object).replace(np.nan, 'None')
# print(df.loc[df['status'] == 'Active'].groupby(['cve_id'])['time_to_resolve'])
# print(len(df.loc[df['status'] == 'Active'].groupby(['cve_id'])))
# df['assessment_date'] = pd.to_datetime(df['assessment_date'])
# df.set_index('assessment_date')
# df['time_to_resolve'] = pd.to_numeric(df['time_to_resolve'])

# severity_summary = df.set_index('assessment_date').groupby([pd.Grouper(freq='d'), 'severity'], as_index=False).size()
# status_summary = df.set_index('assessment_date').groupby([pd.Grouper(freq='d'), 'status'], as_index=False).size()

# json_severity_summary = json.loads(severity_summary.to_json(date_format='iso'))
# json_status_summary = json.loads(status_summary.to_json(date_format='iso'))
# json_mttr_summary = json.loads(mttr_summary.to_json(date_format='iso'))

# time_resolve = df.loc[(df['status'] == 'Fixed')]['time_to_resolve'].mean()
# print(time_resolve)
# print(df[df.groupby(['cve_id']).assessment_date.transform('max') == df['assessment_date']])
