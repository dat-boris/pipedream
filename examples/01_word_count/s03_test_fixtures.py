#!/usr/bin/env python

"""
This is how we would create the text fixture for each part of examples
"""
import logging
logging.basicConfig(level=logging.INFO)

import s02_functional

from pipedream import pipeline

from pipedream import test as pipeline_test
from pipedream.store import PipelineStore

from testdata import EXAMPLE_DATA, run_example

def demo_test_fixture():
    store = PipelineStore()
    # generate the tests
    create_fixture_pipeline = pipeline.compose_pipe([
            s02_functional.emit_words,
            s02_functional.filter_empty_word,
            s02_functional.count_words
        ],
        wrapper=store.save_fixture
    )

    test_data = EXAMPLE_DATA[1]
    print(u"Running '{}' through data pipeline fixture".format(test_data))
    create_fixture_pipeline(test_data)

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
