import logging
from itertools import izip, tee
from functools import reduce, wraps
from inspect import isgeneratorfunction

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
            self.data_stack_trace = []
            return x
        #TODO: save stack trace globally

        return self.apply(
            input,
            wrapper=error_store.save_fixture,
            final_step=clear_stacktrace
        )

    def monitor_step(self, step_func, validate_func):
        """
        This will handle the stack trace of the error
        """
        if (isgeneratorfunction(step_func)):
            @wraps(step_func)
            def wrapper(input, **kwargs):
                i1, i2 = tee(input)
                for i,o in izip(i1, step_func(i2)):
                    try:
                        validate_func(o)
                    except AssertionError as e:
                        logger.error("Seen error: {}".format(e))
                        self.found_error = True
                    self.data_stack_trace.append(o)
                    yield o
            return wrapper
        else:
            @wraps(step_func)
            def func_wrapper(input, **kwargs):
                output = step_func(input)
                try:
                    validate_func(output)
                except AssertionError as e:
                    logger.error("Seen error: {}".format(e))
                    self.found_error = True
                self.data_stack_trace.append(output)
                return output
            return func_wrapper


def test_step(step_function, store):
    """
    Return the step function
    """
    for input, expected in store.all_data_for(step_function):
        logger.info(u"[TEST] Testing {} expects {}".format(input, expected))
        if (isgeneratorfunction(step_function)):
            assert list(step_function(input))==expected
        else:
            assert step_function(input)==expected
        logger.info(u"[TEST] Test passed for {}".format(step_function.__name__))
