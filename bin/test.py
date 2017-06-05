#! /Users/jhefner/python_dev/uw_python/project/bin/python
from slacksible import (cli_parser,
                        build_bot_config,
                        setup_logger,
                        Slacksible)
# import os
# import types
# import logging
import sys
import inspect


def test_cli_parser():
    parser = cli_parser(['-v'])
    print("parser: ", parser)
    assert parser.verbose == 1

def test_build_bot_config():
    config = build_bot_config(cli_parser(['-v']), sys.argv[1])
    print("config: ", config)
    assert config["verbose"] == 1

def test_setup_logger():
    logger = setup_logger("test_log_name", "test_log_file")
    print("isclass: ", inspect.isclass(type(logger)))
    assert inspect.isclass(type(logger)) == True

def test_slacksible_class():
    config = build_bot_config(cli_parser(['-v']), sys.argv[1])
    bot = Slacksible(**config)
    print("bot: ", bot)
    assert inspect.isclass(type(bot)) == True