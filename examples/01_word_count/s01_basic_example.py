#!/usr/bin/env python

"""
Basic examples showing word count concepts
"""

import six
import re

from collections import Counter

import sys
sys.path.append('../..')

from testdata import EXAMPLE_DATA, run_example

#--------------------
# Example 1 - niave example
#--------------------

RE_SPACE = re.compile('\s')

def count(stream):
    """
    How we currently do wordcount
    """
    counter = Counter()
    word = ''
    for i,char in enumerate(iter(lambda: stream.read(1), '')):
        if char is None:
            break
        if RE_SPACE.match(char):
            if word:
                counter[word] += 1
                word = ''
        else:
            word += char
    if word:
        counter[word] += 1
    return counter

RE_CHAR = re.compile('\w')

def count_better_parser(stream):
    """
    How we currently do wordcount with unicode
    - edge case: unicode
    """
    counter = Counter()
    word = ''
    for i,char in enumerate(iter(lambda: stream.read(1), '')):
        if char is None:
            break
        if not RE_CHAR.match(char):
            if word:
                counter[word] += 1
                word = ''
        else:
            word += char
    if word:
        counter[word] += 1
    return counter


if __name__=='__main__':
    run_example(1, count)
    run_example(2, count_better_parser)
