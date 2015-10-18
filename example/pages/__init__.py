# -*- coding: utf-8 -*-
import os
import importlib
from pprint import pprint

__all__ = [x.replace('.py', '') for x in os.listdir(__file__.replace(os.path.basename(__file__), ''))
           if x.endswith('.py') and x != '__init__.py']
for i in __all__:
    importlib.import_module('.' + i, __name__)


