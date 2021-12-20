from __future__ import print_function

from .filter_handler import filter_handler
import logging
from datetime import datetime, timedelta
import pandas as pd
import json
import os
from ipaddress import IPv4Address, IPv6Address

module_path = os.path.abspath(os.path.dirname(__file__))

class laceworkcli_s3_connections_summary_filter_handler(filter_handler):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def ip_apply(self, row):
        try:
            host = IPv4Address(row)
        except:
            host = IPv6Address(row)
        return host

    def filter(self,df):
        rfc1918 = "(?:(?:192\.)(?:(?:168\.)(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.)(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:10\.)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){2}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))|(?:(?:127\.)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){2}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))|(?:(?:172\.)(?:(?:1[6-9]|2[0-9]|3[0-1])\.)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))"

        df['INTERNAL_DST'] = df['DST_IP_ADDR'].str.contains(rfc1918, regex = True)
        df['INTERNAL_SRC'] = df['SRC_IP_ADDR'].str.contains(rfc1918, regex = True)

        df['CREATED_TIME'] = pd.to_datetime(df['CREATED_TIME'])
        df = df.loc[df['INTERNAL_SRC'] == False]
        
        # data sum
        #status_summary = df.set_index('CREATED_TIME').groupby([pd.Grouper(freq='d')], as_index=True).sum().reset_index()
        
        ports_summary = df.set_index('CREATED_TIME').groupby([pd.Grouper(freq='d'), 'MID', 'SRC_IP_ADDR', 'DST_IP_ADDR', 'SRC_PORT', 'DST_PORT'], as_index=False).size().rename(columns={"size": "count"})
        self.logger.info(ports_summary)

        return ports_summary