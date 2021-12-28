#!/usr/bin/env python3

from __future__ import print_function

import argparse
from pyfiglet import Figlet

from custom_reports.reports import reports

import logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)s - %(message)s')

def main():
    ''' Parsing inputs '''
    ver = "0.0.3"
    dsc = "Custom Reports"
    
    print(Figlet(font="3-d").renderText("CUSTOM REPORTS"))
    print("{0} [{1}]\n".format(dsc,ver))

    parser = argparse.ArgumentParser(description=dsc)
    parser.add_argument('--config', required=True, help='path to config file')
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    logger.info("Starting configuration parsing...")
    reports(args.config)

if __name__ == '__main__':
    main()