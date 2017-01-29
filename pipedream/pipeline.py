import logging
from copy import copy
from inspect import isgeneratorfunction
from functools import reduce
from .store import PipelineStore
from .utils import wrap_function

logger = logging.getLogger(__name__)


class Pipeline(object):
    """
    A data pipeline example
    """
    def __init__(self, funcs=None):
        self.funcs = []
        if funcs is not None:
            self.set_steps(funcs)

        self.current_data_store = None
        self.data_stack_trace = []
        self.errors = []
        self.error_prefix = None

    def set_steps(self, funcs):
        self.funcs = list(funcs)

    def apply(self, input, wrapper=None, final_step=None):
        """
        Compose a pipeline together
        """
        func_list = self.funcs
        if wrapper:
            if wrapper is not None:
                func_list = [wrapper(f) for f in self.funcs]

        if final_step:
            func_list.append(final_step)

        # http://stackoverflow.com/questions/38755702/pythonic-way-to-chain-python-generator-function-to-form-a-pipeline
        return reduce(lambda f, g : g(f), func_list, input)

    def monitor_apply(self, input, error_prefix=None):
        """
        Monitoring pipeline apply

        - for each step, store the input and output
        - if seen error, save the stack trace at the end
        """
        self.error_prefix = error_prefix
        self.current_data_store = PipelineStore()

        def callback(input, output, f):
            key = self.current_data_store.store_put(f, input, output)
            self.data_stack_trace.append(key)

        return self.apply(
            input,
            wrapper=lambda f: wrap_function(f, callback)
        )

    def monitor_step(self, step_func, *validate_funcs):
        """
        This will handle the stack trace of the error
        """
        def validate(i, o, f):
            try:
                for v in validate_funcs:
                    v(o)
            except AssertionError as e:
                self._trigger_error(e)

        return wrap_function(step_func, validate)

    def _trigger_error(self, e):
        if self.error_prefix:
            logger.error("Seen error: {}".format(e))
            self.errors.append(copy(self.data_stack_trace))
            error_store_name = "{}{}".format(self.error_prefix, len(self.errors))
            self.current_data_store.copy_to(error_store_name)


def test_step(step_function, store):
    """
    Return the step function
    """
    for input, expected in store.all_data_for(step_function):
        logger.info(u"[TEST] Testing {} expects {}".format(input, expected))
        if (isgeneratorfunction(step_function)):
            output = list(step_function(input))
            # A small hack to avoid terminator position
            assert expected in output, \
                "Expect {}->{}, got {}".format(input, expected, output)
        else:
            assert step_function(input)==expected
        logger.info(u"[TEST] Test passed for {}".format(step_function.__name__))
