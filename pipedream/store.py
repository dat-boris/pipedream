import six
import os
import logging
import ast

from functools import reduce, wraps
from simplekv.fs import FilesystemStore
from inspect import isgeneratorfunction

logger = logging.getLogger(__name__)

class PipelineStore(object):
    """
    A class represent the pipeline store
    """
    def __init__(self, path='./pipeline_store'):
        if not os.path.exists(path):
            os.makedirs(path)
        self.store = FilesystemStore(path)

    def save_fixture(
            self,
            step_func,
            input_key_func=None
            ):
        """
        A Wrapper function which saves each part into setting
        """
        if isgeneratorfunction(step_func):
            @wraps(step_func)
            def generator_wrapper(input, **kwargs):
                output_list = []
                for output in step_func(input):
                    yield output
                    output_list.append(output)
                self.store_put(step_func, input, output_list, input_key_func=input_key_func)
            return generator_wrapper

        else:
            @wraps(step_func)
            def func_wrapper(input, **kwargs):
                output = step_func(input)
                self.store_put(step_func, input, output, input_key_func=input_key_func)
                return output
            return func_wrapper

    def store_put(self, step_func, input, output, input_key_func=None):
        key = self.gen_key_from_input(step_func, input, input_key_func)
        logger.info("[PD] Saving to store key: {} - {}".format(key, output))
        self.store.put(key, self.serialize((input, output)))

    def gen_key_from_input(self, step_func, input, input_key_func=None):
        """
        Parameters
        ----------
        step_func: string or function
            The function to be consuming the input.
        """
        if isinstance(step_func, six.string_types):
            func_name = step_func
        else:
            func_name = self._func_name(step_func)
        if input_key_func is None:
            input_key_func = lambda x: hash(repr(x))
        return "{}.{}".format(func_name, input_key_func(input))

    @staticmethod
    def _func_name(func):
        return func.__name__

    def list(self):
        return [k.split('.', 1) for k in self.store.keys() if k]

    def all_data_for(self, step_function):
        """
        Return a list of test data for the specific functions
        """
        for func_name, input_key in self.list():
            if func_name == self._func_name(step_function):
                yield self.deserialize(
                            self.store.get(
                                "{}.{}".format(func_name, input_key)
                            ))

    def serialize(self, data):
        return repr(data)

    def deserialize(self, data):
        return ast.literal_eval(data)

    # def review(key='', store='prod'):
    #     pass

    # def add_fixture(src, dest, key=None):
    #     pass
