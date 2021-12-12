#!/usr/bin/env python3

import pandas as pd

data = [
    {
        "assessment_date": '2021-11-10T00:00:00Z',
        "cve_id": "CVE-2019-12735",
        "name": "vim",
        "package": "debian:9",
        "status": "active",
        "time_to_resolve": "None",
        "severity": "high"
    },
    {
        "assessment_date": '2021-11-10T00:00:00Z',
        "cve_id": "CVE-2019-3462",
        "name": "apt",
        "package":	"debian:9",
        "status": "fixed",
        "time_to_resolve": "200880",
        "severity": "high"
    },
    {
        "assessment_date": '2021-11-10T00:00:00Z',
        "cve_id": "CVE-2018-1111",
        'name': "dhclient",
        "namespace": "rhel:7",
        "status": "active",
        "time_to_resolve": "None",
        "severity": "critical"
    },
    {
        "assessment_date": '2021-11-10T00:00:00Z',
        "cve_id": "CVE-2019-14287",
        'name': "sudo",
        "namespace": "debian:9",
        "status": "active",
        "time_to_resolve": "None",
        "severity": "medium"
    },
    {
        "assessment_date": '2021-11-10T00:00:00Z',
        "cve_id": "CVE-2018-20969",
        "name": "patch",
        "namespace": "debian:9",
        "status": "active",
        "time_to_resolve": "None",
        "severity": "low"
    },
    
    {
        "assessment_date": '2021-11-11T00:00:00Z',
        "cve_id": "CVE-2019-12735",
        "name": "vim",
        "package": "debian:9",
        "status": "active",
        "time_to_resolve": "None",
        "severity": "high"
    },
    {
        "assessment_date": '2021-11-11T00:00:00Z',
        "cve_id": "CVE-2019-3462",
        "name": "apt",
        "package":	"debian:9",
        "status": "fixed",
        "time_to_resolve": "200880",
        "severity": "high"
    },
    {
        "assessment_date": '2021-11-11T00:00:00Z',
        "cve_id": "CVE-2018-1111",
        'name': "dhclient",
        "namespace": "rhel:7",
        "status": "fixed",
        "time_to_resolve": "200880",
        "severity": "critical"
    },
    {
        "assessment_date": '2021-11-11T00:00:00Z',
        "cve_id": "CVE-2019-14287",
        'name': "sudo",
        "namespace": "debian:9",
        "status": "active",
        "time_to_resolve": "None",
        "severity": "medium"
    },
    {
        "assessment_date": '2021-11-11T00:00:00Z',
        "cve_id": "CVE-2018-20969",
        "name": "patch",
        "namespace": "debian:9",
        "status": "active",
        "time_to_resolve": "None",
        "severity": "low"
    },
    {
        "assessment_date": '2021-11-11T00:00:00Z',
        "cve_id": "CVE-2018-14618",
        "name": "curl",
        "namespace": "debian:9",
        "status": "active",
        "time_to_resolve": "None",
        "severity": "low"
    },
]

df = pd.DataFrame(data)
df['assessment_date']= pd.to_datetime(df['assessment_date'])

severity_summary = df.set_index('assessment_date').groupby([pd.Grouper(freq='d'), 'severity']).size()
status_summary = df.set_index('assessment_date').groupby([pd.Grouper(freq='d'), 'status']).size()

print(severity_summary)