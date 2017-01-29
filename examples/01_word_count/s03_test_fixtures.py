#!/usr/bin/env python

"""
This is how we would create the text fixture for each part of examples
"""
import logging
logging.basicConfig(level=logging.INFO)

import s02_functional

from pipedream import pipeline
from pipedream.store import PipelineStore

from testdata import EXAMPLE_DATA

def demo_test_fixture():
    store = PipelineStore()
    # generate the tests
    fixture_pipeline = pipeline.Pipeline([
            s02_functional.emit_words,
            s02_functional.filter_empty_word,
            s02_functional.count_words
        ]
    )

    test_data = EXAMPLE_DATA[1]
    print(u"Running '{}' through data pipeline fixture".format(test_data))
    fixture_pipeline.apply(
        test_data,
        wrapper=store.save_fixture
    )

    # py.test - boom!
    # run the tests
    print(u"Testing emit_words parser")
    pipeline.test_step(
        s02_functional.emit_words,
        store=store
    )

    print(u"Test pass!")

if __name__=='__main__':
    demo_test_fixture()
