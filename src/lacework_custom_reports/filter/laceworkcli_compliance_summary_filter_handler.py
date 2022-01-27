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
                    "report_account": "{0}:{1}".format(r['accountAlias'], r['accountId']),
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
                    "report_account": "{0}:{1}:{2}:{3}".format(
                        r['organizationId'],
                        r['organizationName'],
                        r['projectId'],
                        r['projectName']
                    ),
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
                    "report_account": "{0}:{1}:{2}:{3}".format(
                        r['tenantId'],
                        r['tenantName'],
                        r['subscriptionId'],
                        r['subscriptionName']
                    ),
                    "tenantId": r['tenantId'],
                    "tenantName": r['tenantName'],
                    "subscriptionId": r['subscriptionId'],
                    "subscriptionName": r['subscriptionName'],
                    "reportTime": r['reportTime'],
                    "reportTitle": r['reportTitle'],
                    "reportType": r['reportType'],
                    "summary": r['summary'],
                    "resources": ", ".join(resources)
                }

            # appden the summary fields and then drop summary
            tdf = pd.DataFrame(tdf)
            tdf = tdf.join(pd.json_normalize(tdf.summary))
            tdf.drop(columns=['summary'], inplace=True)
            tdf['compliance_coverage'] = int(
                round(tdf['num_compliant']/(tdf['num_compliant']+tdf['num_not_compliant'])*100, 0)
            )
            dfs.append(tdf)

        # concat all results into single dataframe
        if len(dfs) > 0:
            df = pd.concat(dfs, ignore_index=True)
            self.logger.info(df.head(3))

            # total compliant
            total_compliant = int(df['num_compliant'].sum())
            total_not_compliant = int(df['num_not_compliant'].sum())
            total_accounts = len(df.index)
            total_compliance_coverage = int(round(total_compliant/(total_compliant+total_not_compliant)*100, 0))

            # data summary
            data_summary = {
                "rows": len(df.index),
                "total_compliant": total_compliant,
                "total_not_compliant": total_not_compliant,
                "total_accounts": total_accounts,
                "total_compliance_coverage": total_compliance_coverage,
                "account_compliance": json.loads(df[[
                    'report_account',
                    'num_compliant',
                    'num_not_compliant',
                    'compliance_coverage'
                ]].to_json(date_format='iso'))
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
