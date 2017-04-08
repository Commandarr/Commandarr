# #############################################################################
# File Name: test_commons.py
# Author: Todd Johnson
# Creation Date: 08/04/2017
#
# Description: [To be completed]
#
# Offical website: https://www.comandarr.github.io
# Github Source: https://www.github.com/comandarr/comandarr/
# Readme Source: https://www.github.com/comandarr/comandarr/README.md
#
# #############################################################################

# Import required modules
import pytest
import yaml
from comandarr import commons

from definitions import CONFIG_PATH
config = yaml.safe_load(open(CONFIG_PATH))


def test_cleanUrl():
    assert commons.cleanUrl('http://test.com?term=The Big Bang Theory') == \
        'http://test.com?term=The%20Big%20Bang%20Theory'
