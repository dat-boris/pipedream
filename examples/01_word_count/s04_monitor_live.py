#!/usr/bin/env python

"""
How we can send signal and review incidence
"""
import logging
logging.basicConfig(level=logging.INFO)

import s02_functional

from testdata import BAD_INPUT

from pipedream import pipeline

from pipedream import test as pipeline_test
from pipedream.store import PipelineStore


def demo_broken_monitoring():

    error_store = PipelineStore('./error_store')

    def check_word_maxlen(word):
        assert 0 < len(word) < 40, "Expect be less than 40 chars"

    def check_number_of_words(word):
        assert len(word) >= 3,"Expect have more than 3 words in a paragraph"

    monitored_pipeline = pipeline.compose_pipe([
        s02_functional.emit_words,
        pipeline.monitor_step(
            s02_functional.filter_empty_word,
            check_word_maxlen,
            error_store=error_store
        ),
        pipeline.monitor_step(
            s02_functional.count_words,
            check_number_of_words,
            error_store=error_store
        ),
    ])
    monitored_pipeline(BAD_INPUT[0])

    # Run unexpected input
    errors = error_store.list()
    print("You have following errors: {}".format(errors))

    # pipeline_store.add_fixture('prod', 'test', errors[0])

    # test_fixture_pipeline = pipeline.compose_pipe([
    #         s02_functional.emit_words,
    #         s02_functional.filter_empty_word,
    #         s02_functional.count_words
    #     ],
    #     wrapper=pipeline_test.test_step
    # )


if __name__ == '__main__':
    demo_broken_monitoring()
