# -*- coding: utf-8 -*-

"""
Test data shared between examples
"""

import io

EXAMPLE_DATA = [
    u"Hello world! Hello friends!",
    u"Hello world🌏, Hello friends🍕",
]

def run_example(i, count_function):
    print("Running example: {}".format(i))
    for input_str in EXAMPLE_DATA:
        print(count_function(io.StringIO(input_str)))
