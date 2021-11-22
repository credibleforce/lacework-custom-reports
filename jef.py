#!/usr/bin/env python3

from __future__ import print_function

import os
import argparse
import json
import jinja2

class JustEffectivelyFormatting():
    # init method or constructor   
    def __init__(self, data, template, output):  
        self.data = data  
        self.template = template
        self.output = output
      
    # Sample Method   
    def format(self):  
        loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(self.template))
        env = jinja2.Environment(loader=loader)
        template = env.get_template(os.path.basename(self.template))
        with open(self.data) as json_file:
            data = json.load(json_file)
            with open(self.output,'w') as output_file:
                output_file.write(template.render(items=data))

def main():
    ''' Parsing inputs '''
    dsc = "Just Effectively Formatting"

    parser = argparse.ArgumentParser(description=dsc)
    parser.add_argument('--data', required=True, help='data source path')
    parser.add_argument('--template', required=True, help='template file')
    parser.add_argument('--output', required=True, help='output file')
    args = parser.parse_args()

    j = JustEffectivelyFormatting(data=args.data,template=args.template,output=args.output)  
    j.format()  


if __name__ == '__main__':
    main()