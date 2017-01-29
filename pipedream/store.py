import six
import os
import logging
import ast

from functools import reduce, wraps
from simplekv.fs import FilesystemStore
from inspect import isgeneratorfunction

from .utils import wrap_function

logger = logging.getLogger(__name__)


class PipelineStore(object):
    """
    A class represent the pipeline store
    """
    def __init__(self, path='./pipeline_store', input_key_func=None):
        if not os.path.exists(path):
            os.makedirs(path)
        self.store = FilesystemStore(path)
        self.clear()

        self.input_key_func = input_key_func
        if self.input_key_func is None:
            self.input_key_func = lambda x: hash(repr(x))

    def save_fixture(self, step_func):
        """
        A Wrapper function which saves each part into setting
        """
        def callback(input, output, f):
            self.store_put(f, input, output)

        return wrap_function(step_func, callback)

    def store_put(self, step_func, input, output):
        key = self.gen_key_from_input(step_func, input)
        logger.info("[PD] Saving to store key: {} - {}".format(key, output))
        self.store.put(key, self.serialize((input, output)))
        return key

    def gen_key_from_input(self, step_func, input):
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
        return "{}.{}".format(func_name, self.input_key_func(input))

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

    def get_values(self, keys=None):
        if keys is None:
            keys = self.list()
        return [
            self.store.get("{}.{}".format(func_name, input_key))
            for func_name, input_key in keys
        ]

    def serialize(self, data):
        return repr(data)

    def deserialize(self, data):
        return ast.literal_eval(data)

    def clear(self):
        for k in self.store:
            self.store.delete(k)