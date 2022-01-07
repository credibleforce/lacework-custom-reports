from __future__ import print_function

from .filter_handler import filter_handler
import logging
import pandas as pd
import json
import os

module_path = os.path.abspath(os.path.dirname(__file__))


class laceworkcli_compliance_summary_filter_handler(filter_handler):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def filter(
                self,
                data,
                dataset=None,
                datasets=None
               ):
        # check to see if we were passed a dataframe
        # if data is not pd.DataFrame:
        #     df = pd.DataFrame(data)
        # else:
        #     df = data

        self.logger.info("Found: {0} results".format(len(data)))

        dfs = []
        csp_type = data['csp_type']

        for r in data.get('reports', {}):
            # accumulate resources
            resources = []
            for rec in r['recommendations']:

                if rec.get('violations') is not None:
                    vis = rec.get('violations')
                else:
                    vis = []

                for v in vis:
                    res = "{0} ({1}) {2}".format(
                        v.get('resource'),
                        v.get('region', 'not associated'),
                        v.get('reasons'))
                    if res not in resources:
                        resources.append(res)

            if csp_type == "aws":
                tdf = {
                    "account": r['accountAlias'],
                    "accountId": r['accountId'],
                    "reportTime": r['reportTime'],
                    "reportTitle": r['reportTitle'],
                    "reportType": r['reportType'],
                    "summary": r['summary'],
                    "resources": ", ".join(resources)
                }
            elif csp_type in ["google", "gcp"]:
                tdf = {
                    "organizationId": r['organizationId'],
                    "organizationName": r['organizationName'],
                    "projectId": r['projectId'],
                    "projectName": r['projectName'],
                    "reportTime": r['reportTime'],
                    "reportTitle": r['reportTitle'],
                    "reportType": r['reportType'],
                    "summary": r['summary'],
                    "resources": ", ".join(resources)
                }
            elif csp_type in ["az", "azure"]:
                tdf = {
                    "tenantId": r['tenantId'],
                    "tenantName": r['tenantName'],
                    "subscriptionId": r['subscriptionName'],
                    "subscriptionName": r['subscriptionName'],
                    "reportTime": r['reportTime'],
                    "reportTitle": r['reportTitle'],
                    "reportType": r['reportType'],
                    "summary": r['summary'],
                    "resources": ", ".join(resources)
                }

            dfs.append(pd.DataFrame(tdf))

        # concat all results into single dataframe
        if len(dfs) > 0:
            df = pd.concat(dfs, ignore_index=True)
            self.logger.info(df.head(3))

            # data summary
            data_summary = {
                "rows": len(df.index)
            }

            # convert to from dataframe
            json_data = json.loads(df.to_json(date_format='iso'))
        else:
            # data summary
            data_summary = {
                "rows": len(dfs.index)
            }

            # convert to from dataframe
            json_data = json.loads(pd.DataFrame(dfs).to_json(date_format='iso'))

        return json_data, data_summary
