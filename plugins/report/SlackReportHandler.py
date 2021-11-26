from plugins.report.ReportHandler import ReportHandler
import os
from slack import WebClient
from slack.errors import SlackApiError

import logging
logging.basicConfig(level=logging.DEBUG)

class SlackReportHandler(ReportHandler):
    def generate(self):
        slack_token = os.environ["SLACK_API_TOKEN"]
        #slack_token = self.report.token
        client = WebClient(token=slack_token)

        try:
            response = client.chat_postMessage(
                channel=self.report['channel'],
                text='''```{0}```'''.format(self.datasets),
                attachments=[{"pretext": "pre-hello", "text": "text-world"}]
            )
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'