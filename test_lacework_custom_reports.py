import argparse

import pytest

from lacework_custom_reports import __main__ as main


def test_main_default():
    args = argparse.Namespace(account=None,
                              subaccount=None,
                              api_key=None,
                              api_secret=None,
                              profile=None,
                              days=None,
                              hours=0,
                              registry=None,
                              rescan=None,
                              list_only=None,
                              daemon=None,
                              debug=None)
    main.run(args)


def test_main_config_fail():
    args = argparse.Namespace(account='testing',
                              subaccount=None,
                              api_key=None,
                              api_secret=None,
                              profile=None,
                              days=None,
                              hours=0,
                              registry=None,
                              rescan=None,
                              list_only=None,
                              daemon=None,
                              debug=None)
    with pytest.raises(Exception):
        main.run(args)
