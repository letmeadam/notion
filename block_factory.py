import logging


class BlockFactory(object):
    _block_classes = {}
    _base_class = None

    @classmethod
    def get(cls, block_type: str):
        block_class = cls._block_classes.get(block_type)
        if block_class is None:
            logging.warning(f"Unknown block type: {block_type}")
            return cls._base_class
        return block_class

    @classmethod
    def register(cls, block_type: str):
        def inner_wrapper(wrapped_class):
            cls._block_classes[block_type] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def register_base_class(cls):
        def inner_wrapper(wrapped_class):
            cls._base_class = wrapped_class
            return wrapped_class

        return inner_wrapper


from . import block
from .blocks import *
