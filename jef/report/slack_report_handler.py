from ssl import CHANNEL_BINDING_TYPES
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
        attachment_from_template = None
        if self.attachment_template is not None:
            self.logger.info("Attachment template defined - parsing...")
            attachment_from_template = self.attachment_template.render(items=self.datasets)

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
            
            # if we have a templated attachment upload content to same thread
            if self.attachment_template is not None:
                try:
                    upload_reponse = client.files_upload(
                        channels=self.report['channel'],
                        content=attachment_from_template,
                        filename=self.report['attachment_name'],
                        initial_comment=self.report['attachment_comment'],
                        thread_ts=response['ts']
                    )
                except SlackApiError as e:
                    self.logger.error(e.response["error"]) # str like 'invalid_auth', 'channel_not_found'
                
        except SlackApiError as e:
            self.logger.error(e.response["error"])
            # You will get a SlackApiError if "ok" is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'