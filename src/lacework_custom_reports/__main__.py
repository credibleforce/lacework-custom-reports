from __future__ import print_function

import argparse
from pyfiglet import Figlet

from .app import reports

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)s - %(message)s'
    )


def run(args_override=None):
    ''' Parsing inputs '''
    ver = "0.0.7"
    dsc = "Custom Reports"

    print(Figlet(font="3-d").renderText("CUSTOM REPORTS"))
    print("{0} [{1}]\n".format(dsc, ver))

    parser = argparse.ArgumentParser(description=dsc)
    parser.add_argument('--config', required=True, help='path to config file')

    if args_override is not None:
        args = args_override
    else:
        args = parser.parse_args()

    logger = logging.getLogger(__name__)
    logger.info("Starting configuration parsing...")
    reports(args.config)


if __name__ == '__main__':
    run()
