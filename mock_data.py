#!/usr/bin/python3

"""
Script to provide mock input to the script to test regex results and other stuff.

Requires xdcc_anime.py in the same folder.
"""

__author__ = "nightly5"
__license__ = "MIT"

import re
import xdcc_anime

def _mock_data():
    with (
        open("ARUTHA-BATCH.1080p.xdcc.txt") as f1,
        open("CR-ARUTHA.NEW.xdcc.txt") as f2
    ):
        f1_txt = f1.read()
        f2_txt = f2.read()
    args_list = (
        (
            re.escape("vinland saga s2"), # test for lower case
            "1080p",
            "CR-HOLLAND|NEW",
            f2_txt
        ),
        (
            re.escape("tokyo revengers"), # test for ep with 01v2 format
            "1080p",
            "ARUTHA-BATCH|1080p",
            f1_txt
        ),
        (
            re.escape("tok"), # test for partial anime name
            "1080p",
            "ARUTHA-BATCH|1080p",
            f1_txt
        ),
        (
            re.escape("yahari"), # horriblesubs packs
            "1080p",
            "ARUTHA-BATCH|1080p",
            f1_txt
        )
    )
    for i, args in enumerate(args_list):
        print(f"\nMock {i+1}:")
        xdcc_anime.process_data(*args)

if __name__ == "__main__":
    _mock_data()
