from slack.web.slack_response import SlackResponse
from .report_handler import report_handler
from slack import WebClient
from slack.errors import SlackApiError
import json
import os

module_path = os.path.abspath(os.path.dirname(__file__))

class slack_report_handler(report_handler):
    def generate(self):
        # as we can't submit json directory with the client we parse first and then supply args
        message_from_template = self.template.render(items=self.datasets,channel=self.report['channel'])
        slack_message = json.loads(message_from_template)
        client = WebClient(token=self.report['token'])

        try:
            response = client.chat_postMessage(
                channel=slack_message['channel'],
                text=(slack_message['text'] if 'text' in slack_message.keys() is not None else None),
                attachments=(slack_message['attachments'] if 'attachments' in slack_message.keys() is not None else None),
                blocks=(slack_message['blocks'] if 'blocks' in slack_message.keys() is not None else None)
            )
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'