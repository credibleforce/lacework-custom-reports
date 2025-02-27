from __future__ import print_function

from .filter_handler import filter_handler
import logging
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
        except Exception:
            host = IPv6Address(row)
        return host

    def filter(
                self,
                data,
                dataset=None,
                datasets=None
               ):
        rfc1918 = '(?:(?:192\\.)(?:(?:168\\.)(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\\.)' \
            '(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))' \
            '|(?:(?:10\\.)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){2}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))' \
            '|(?:(?:127\\.)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){2}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))' \
            '|(?:(?:172\\.)(?:(?:1[6-9]|2[0-9]|3[0-1])\\.)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.)' \
            '(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'

        data['INTERNAL_DST'] = data['DST_IP_ADDR'].str.contains(rfc1918, regex=True)
        data['INTERNAL_SRC'] = data['SRC_IP_ADDR'].str.contains(rfc1918, regex=True)

        data['CREATED_TIME'] = pd.to_datetime(data['CREATED_TIME'])
        df = data.loc[data['INTERNAL_SRC'] is False]

        # data sum
        # status_summary = df.set_index('CREATED_TIME').groupby([pd.Grouper(freq='d')], as_index=True).sum().reset_index()

        df = df.set_index('CREATED_TIME').groupby([
            pd.Grouper(freq='d'),
            'MID',
            'SRC_IP_ADDR',
            'DST_IP_ADDR',
            'SRC_PORT',
            'DST_PORT'],
            as_index=False).size().rename(columns={"size": "count"})

        self.logger.info(df)

        # data summary
        data_summary = {
            "rows": len(df.index)
        }

        # convert to from dataframe
        json_data = json.loads(df.to_json(date_format='iso'))

        return json_data, data_summary
