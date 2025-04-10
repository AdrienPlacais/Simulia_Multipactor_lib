"""Define a base singleton pattern class."""

import logging
from abc import ABC


class SingletonMeta(type, ABC):
    """Define singleton template to inherit from."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Create instance only if not already exists."""
        if cls not in cls._instances:
            logging.info("Called __call__ (None)")
            cls._instances[cls] = super().__call__(*args, **kwargs)
        else:
            logging.info("Called __call__ (not None)")

        return cls._instances[cls]
