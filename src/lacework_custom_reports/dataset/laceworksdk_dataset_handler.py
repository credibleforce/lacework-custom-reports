from __future__ import print_function

from .dataset_handler import dataset_handler
import os

from datetime import datetime, timedelta
from laceworksdk import LaceworkClient

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

        # pass through a filter for parsing/manipulation if required
        if self.filterClass is not None:
            json_data, data_summary = self.filterClass().filter(result.get('data'), dataset=self.dataset)
        else:
            json_data = result.get('data')
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
