import logging
from inspect import isgeneratorfunction
from functools import reduce
from .store import wrap_function

logger = logging.getLogger(__name__)


class Pipeline(object):
    """
    A data pipeline example
    """
    def __init__(self, funcs=None):
        self.funcs = []
        if funcs is not None:
            self.set_steps(funcs)
        self.data_stack_trace = []
        self.found_error = False
        self.errors = []

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

    def monitor_apply(self, input, error_store=None):
        """
        Monitoring pipeline apply

        - for each step, store the input and output
        - if seen error, save the stack trace at the end
        """
        def clear_stacktrace(x):
            if self.found_error:
                logger.error("Found error: see stack trace on Pipeline.errors")
                self.errors.append(self.data_stack_trace)
            self.data_stack_trace = []
            return x

        return self.apply(
            input,
            wrapper=error_store.save_fixture,
            final_step=clear_stacktrace
        )

    def monitor_step(self, step_func, validate_func):
        """
        This will handle the stack trace of the error
        """
        def validate(i, o, f):
            try:
                validate_func(o)
            except AssertionError as e:
                logger.error("Seen error: {}".format(e))
                self.found_error = True

        return wrap_function(step_func, validate)


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
