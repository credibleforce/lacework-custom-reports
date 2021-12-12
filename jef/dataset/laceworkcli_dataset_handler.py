from __future__ import print_function

from .dataset_handler import dataset_handler
import json
import subprocess
import os

module_path = os.path.abspath(os.path.dirname(__file__))

class laceworkcli_dataset_handler(dataset_handler):
    def load(self):
        # process args hack
        subaccount = ("--subaccount={0}".format(self.datase['subaccount']) if 'subaccount' in self.dataset.keys() and self.dataset['subaccount'] else "")
        profile = ("--profile={0}".format(self.dataset['profile']) if 'profile' in self.dataset.keys() and self.dataset['profile'] else "")
        api_key = ("--api_key={0}".format(self.dataset['api_key']) if 'api_key' in self.dataset.keys() and self.dataset['api_key'] else "")
        api_secret = ("--api_secret={0}".format(self.dataset['api_secret']) if 'api_secret' in self.dataset.keys() and self.dataset['api_secret'] else "")
        api_token = ("--api_token={0}".format(self.dataset['api_token']) if 'api_token' in self.dataset.keys() and self.dataset['api_token'] else "")
        api_token = ("--organization={0}".format(self.dataset['organization']) if 'organization' in self.dataset.keys() and self.dataset['organization'] else "")
        
        # build command
        command = 'lacework {0} {1} {2} {3} {4} {5} --nocolor --noninteractive --json'.format(
            self.dataset['command'],
            self.dataset['args'],
            subaccount, 
            profile,
            api_key,
            api_secret,
            api_token)
        
        self.logger.debug("Running: {0}".format(command))

        result = json.loads(subprocess.run(command, capture_output=True, text=True, shell=True).stdout)
        self.data = {
            "name": self.dataset.get('name'),
            "data": result,
            "summary": {
                "rows": len(result)
            }
        }