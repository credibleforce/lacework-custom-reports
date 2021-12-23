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

    def filter(self,data,datasets=[]):
        self.logger.info("Found: {0} results".format(len(data)))
        dfs = []
        csp_type = data['csp_type']
        for r in data['reports']:
            if csp_type == "aws":
                tdf = {
                    "account" : r['accountAlias'],
                    "summary" : r['accountId'],
                    "reportTime": r['reportTime'],
                    "reportTitle": r['reportTitle'],
                    "reportType": r['reportType'],
                    "summary" : r['summary']
                }
            elif csp_type in ["google","gcp"]:
                tdf = {
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
                tdf = {
                    "tenantId" : r['tenantId'],
                    "tenantName" : r['tenantName'],
                    "subscriptionId" : r['subscriptionName'],
                    "subscriptionName" : r['subscriptionName'],
                    "reportTime": r['reportTime'],
                    "reportTitle": r['reportTitle'],
                    "reportType": r['reportType'],
                    "summary" : r['summary']
                }
            
            dfs.append(pd.DataFrame(tdf))

        # concat all results into single dataframe
        if len(dfs) > 0:
            df = pd.concat(dfs, ignore_index=True)
            self.logger.info(df)
            return df
        else:
            return pd.DataFrame(dfs)