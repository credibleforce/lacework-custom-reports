from __future__ import print_function

from .filter_handler import filter_handler
import logging
from datetime import datetime, timedelta
import pandas as pd
import json
import os

module_path = os.path.abspath(os.path.dirname(__file__))

class laceworkcli_compliance_summary_filter_handler(filter_handler):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def filter(self,result):
        
        self.logger.info("Found: {0} results".format(len(result)))
        dfs = []
        csp_type = result['csp_type']
        for r in result['reports']:
            if csp_type == "aws":
                data = {
                    "account" : r['accountAlias'],
                    "summary" : r['accountId'],
                    "reportTime": r['reportTime'],
                    "reportTitle": r['reportTitle'],
                    "reportType": r['reportType'],
                    "summary" : r['summary']
                }
            elif csp_type in ["google","gcp"]:
                data = {
                    "organizationId" : r['organizationId'],
                    "organizationName" : r['organizationName'],
                    "projectId" : r['projectId'],
                    "projectName" : r['projectName'],
                    "reportTime": r['reportTime'],
                    "reportTitle": r['reportTitle'],
                    "reportType": r['reportType'],
                    "summary" : r['summary']
                }
            elif csp_type in ["az","azure"]:
                data = {
                    "tenantId" : r['tenantId'],
                    "tenantName" : r['tenantName'],
                    "subscriptionId" : r['subscriptionName'],
                    "subscriptionName" : r['subscriptionName'],
                    "reportTime": r['reportTime'],
                    "reportTitle": r['reportTitle'],
                    "reportType": r['reportType'],
                    "summary" : r['summary']
                }
            
            dfs.append(pd.DataFrame(data))

        # concat all results into single dataframe
        if len(dfs) > 0:
            df = pd.concat(dfs, ignore_index=True)
            self.logger.info(df)
            return df
        else:
            return pd.DataFrame(dfs)