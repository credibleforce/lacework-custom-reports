#!/usr/bin/env python3

import pandas as pd
import json

data = [
    {
        "assessment_date": '2021-11-10T00:00:00Z',
        "cve_id": "CVE-2019-12735",
        "name": "vim",
        "package": "debian:9",
        "status": "Active",
        "time_to_resolve": "None",
        "severity": "high"
    },
    {
        "assessment_date": '2021-11-10T00:00:00Z',
        "cve_id": "CVE-2019-3462",
        "name": "apt",
        "package":	"debian:9",
        "status": "Fixed",
        "time_to_resolve": 200880,
        "severity": "high"
    },
    {
        "assessment_date": '2021-11-10T00:00:00Z',
        "cve_id": "CVE-2018-1111",
        'name': "dhclient",
        "namespace": "rhel:7",
        "status": "Active",
        "time_to_resolve": "None",
        "severity": "critical"
    },
    {
        "assessment_date": '2021-11-10T00:00:00Z',
        "cve_id": "CVE-2019-14287",
        'name': "sudo",
        "namespace": "debian:9",
        "status": "Fixed",
        "time_to_resolve": 9999999,
        "severity": "medium"
    },
    {
        "assessment_date": '2021-11-10T00:00:00Z',
        "cve_id": "CVE-2018-20969",
        "name": "patch",
        "namespace": "debian:9",
        "status": "Active",
        "time_to_resolve": "None",
        "severity": "low"
    },

    {
        "assessment_date": '2021-11-11T00:00:00Z',
        "cve_id": "CVE-2019-12735",
        "name": "vim",
        "package": "debian:9",
        "status": "Fixed",
        "time_to_resolve": 1000,
        "severity": "high"
    },
    {
        "assessment_date": '2021-11-11T00:00:00Z',
        "cve_id": "CVE-2019-3462",
        "name": "apt",
        "package":	"debian:9",
        "status": "Fixed",
        "time_to_resolve": 200880,
        "severity": "high"
    },
    {
        "assessment_date": '2021-11-11T00:00:00Z',
        "cve_id": "CVE-2018-1111",
        'name': "dhclient",
        "namespace": "rhel:7",
        "status": "Fixed",
        "time_to_resolve": 200880,
        "severity": "critical"
    },
    {
        "assessment_date": '2021-11-11T00:00:00Z',
        "cve_id": "CVE-2019-14287",
        'name': "sudo",
        "namespace": "debian:9",
        "status": "Active",
        "time_to_resolve": "None",
        "severity": "medium"
    },
    {
        "assessment_date": '2021-11-11T00:00:00Z',
        "cve_id": "CVE-2018-20969",
        "name": "patch",
        "namespace": "debian:9",
        "status": "Active",
        "time_to_resolve": "None",
        "severity": "low"
    },
    {
        "assessment_date": '2021-11-11T00:00:00Z',
        "cve_id": "CVE-2018-14618",
        "name": "curl",
        "namespace": "debian:9",
        "status": "Active",
        "time_to_resolve": "None",
        "severity": "low"
    },
]

df = pd.DataFrame(data)
df['assessment_date'] = pd.to_datetime(df['assessment_date'])
df['time_to_resolve'] = pd.to_numeric(df['time_to_resolve'])

severity_summary = df.set_index('assessment_date').groupby([pd.Grouper(freq='d'), 'severity'], as_index=False).size()
status_summary = df.set_index('assessment_date').groupby([pd.Grouper(freq='d'), 'status'], as_index=False).size()

json_severity_summary = json.loads(severity_summary.to_json(date_format='iso'))
json_status_summary = json.loads(status_summary.to_json(date_format='iso'))
# json_mttr_summary = json.loads(mttr_summary.to_json(date_format='iso'))

time_resolve = df.loc[(df['status'] == 'Fixed')]['time_to_resolve'].mean()
print(time_resolve)
