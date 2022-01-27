from __future__ import print_function

from .dataset_handler import dataset_handler
import os

from datetime import datetime
from laceworksdk import LaceworkClient
import pandas as pd
import json

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

        # initialize result objects
        json_data = {}
        data_summary = {}

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
        # result = {
        #     'data': [],
        #     'summary': {}
        # }

        query = {
            "timeFilters": {},
            "filters": [],
            "returns": []
        }
        query['timeFilters']['startTime'] = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        query['timeFilters']['endTime'] = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        query['filters'].append(
            {"field": "status", "expression": "eq", "value": "Active"}
        )

        if severity:
            query['filters'].append(
                {"field": "severity", "expression": "eq", "value": severity}
            )
        if fixable:
            query['filters'].append(
                {"field": "fixInfo.fix_available", "expression": "eq", "value": 1}
            )

        query['returns'] = [
            "startTime",
            "endTime",
            "severity",
            "status",
            "vulnId",
            "featureKey",
            "machineTags",
            "fixInfo.fix_available",
            "fixInfo.fixed_version",
            "fixInfo.version_installed"
        ]
        host_vulns = self.lw.vulnerabilities.hosts.search(json=query)

        results = []
        for h in host_vulns:
            for d in h['data']:
                self.logger.info(d['vulnId'])
                results.append(d)

        # convert to data frame
        df = pd.DataFrame(results)
        results = json.loads(df.to_json(date_format='iso'))

        # pass through a filter for parsing/manipulation if required
        if self.filterClass is not None:
            json_data, data_summary = self.filterClass().filter(results, dataset=self.dataset)
        else:
            json_data = results
            data_summary = {
                "rows": len(json_data)
            }

        self.data = {
            "name": self.dataset.get('name'),
            "data": json_data,
            "summary": {
                "report_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "end_time": end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "rows": data_summary.get('rows'),
                "data_summary": data_summary
            }
        }
