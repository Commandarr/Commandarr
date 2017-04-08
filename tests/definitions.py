# #############################################################################
# File Name: definitions.py
# Author: Todd Johnson
# Creation Date: 04/04/2017
#
# Description: Sets global project constants.
#
# Github Source: https://www.github.com/comandarr/comandarr/
# Readme Source: https://www.github.com/comandarr/comandarr/README.md
#
# #############################################################################

import os

# Set Projects Root Directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Set Projects Configuration path
CONFIG_PATH = os.path.join(ROOT_DIR, '../config/config.yaml')
