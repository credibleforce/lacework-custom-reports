from __future__ import print_function

import json
import jsonschema
from jsonschema import validate
import jinja2
import os

module_path = os.path.abspath(os.path.dirname(__file__))

class reports():
    def __init__(self,config):
        self.config = config
        valid, msg = self.load()
        if valid:
            print(msg)
            self.generate()
        else:
            print(msg)
    
    def load(self):
        loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(self.config))
        env = jinja2.Environment(loader=loader)
        template = env.get_template(os.path.basename(self.config))
        self.config = json.loads(template.render(env=os.environ))
        
        return self.validate_json(self.config)

    def generate(self):
        # enumerate reports and render
        for r in self.config['reports']:
            j = report(report=r)

    def get_schema(self):
        """This function loads the given schema available"""
        with open('{0}/schema/reports.schema.json'.format(module_path), 'r') as file:
            schema = json.load(file)
        return schema

    def validate_json(self,json_data):
        execute_api_schema = self.get_schema()
        try:
            validate(instance=json_data, schema=execute_api_schema)
        except jsonschema.exceptions.ValidationError as err:
            return False, err

        return True, "Validated schema successfully"

