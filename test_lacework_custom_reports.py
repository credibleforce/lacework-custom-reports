import argparse

import pytest

from src.lacework_custom_reports import __main__ as main


def test_main_default():
    args = argparse.Namespace(config=None)
    main.run(args)


def test_main_config_fail():
    args = argparse.Namespace()
    with pytest.raises(Exception):
        main.run(args)
