#!/usr/bin/env python

"""
How we can send signal and review incidence
"""
import logging
logging.basicConfig(level=logging.ERROR)

import s02_functional

from pprint import pprint

from testdata import BAD_INPUT

from pipedream import pipeline
from pipedream.store import PipelineStore


def demo_broken_monitoring():

    def check_word_maxlen(word):
        assert 0 < len(word) < 40, "Expect be less than 40 chars"

    class FrequencyValidator(object):
        def __init__(self, max_empty=100):
            self.empty_count = 0
            self.max_empty = max_empty

        def validate(self, word):
            if not word:
                self.empty_count += 1
                if (self.empty_count >= self.max_empty):
                    self.empty_count = 0
                    assert False, \
                        "Do not expect {} consecutive empty words".format(self.max_empty)
            else:
                self.empty_count = 0

    monitored_pipeline = pipeline.Pipeline()

    monitored_pipeline.set_steps([
        monitored_pipeline.monitor_step(
            s02_functional.emit_words,
            FrequencyValidator().validate
        ),
        monitored_pipeline.monitor_step(
            s02_functional.filter_empty_word,
            check_word_maxlen
        ),
        s02_functional.filter_empty_word,
        s02_functional.count_words
    ])

    output = monitored_pipeline.monitor_apply(
        BAD_INPUT[0],
        error_prefix='error_store'
    )

    print(output)

    # Run unexpected input
    print("Inspecting error store: error_store1")
    #print("You have error keys: {}".format(monitored_pipeline.errors[0]))
    error_store = PipelineStore('./error_store1', inspect=True)
    errors = error_store.get_values()
    print("You have following errors:")
    pprint(errors)


if __name__ == '__main__':
    demo_broken_monitoring()
