
import redataprocessing.sreality as rdp

from inspect import getmembers, isfunction

import redataprocessing
from redataprocessing.sreality import *

print(getmembers(rdp, isfunction))

import imp
import os
MODULE_EXTENSIONS = ('.py', '.pyc', '.pyo')

def package_contents(package_name):
    file, pathname, description = imp.find_module(package_name)
    if file:
        raise ImportError('Not a package: %r', package_name)
    # Use a set because some may be both source and compiled.
    return set([os.path.splitext(module)[0]
        for module in os.listdir(pathname)
        if module.endswith(MODULE_EXTENSIONS)])

package_contents("rdp")

get_re_offers("real_estate_from_package.sqlite", category_main="apartments", category_type="sale", locality_region=[])