from __future__ import print_function

import json
import jsonschema
from jsonschema import validate
import jinja2
from .generate import generate
import os
import logging

module_path = os.path.abspath(os.path.dirname(__file__))

class reports():
    def __init__(self,config,plugins=[]):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.plugins = plugins
        valid, msg = self.load()
        if valid:
            self.logger.debug(msg)
            self.generate()
        else:
            self.logger.error(msg)
    
    def load(self):
        loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(self.config))
        env = jinja2.Environment(loader=loader)
        template = env.get_template(os.path.basename(self.config))
        self.config = json.loads(template.render(env=os.environ))
        
        return self.validate_json(self.config)

    def generate(self):
        # enumerate reports and render
        for r in self.config['reports']:
            j = generate(report=r,plugins=self.plugins)

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