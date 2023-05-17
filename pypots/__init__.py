"""
PyPOTS package.
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GPL-v3


# PyPOTS version
#
# PEP0440 compatible formatted version, see:
# https://www.python.org/dev/peps/pep-0440/
# Generic release markers:
# X.Y
# X.Y.Z # For bugfix releases
#
# Admissible pre-release markers:
# X.YaN # Alpha release
# X.YbN # Beta release
# X.YrcN # Release Candidate
# X.Y # Final release
#
# Dev branch marker is: 'X.Y.dev' or 'X.Y.devN' where N is an integer.
# 'X.Y.dev0' is the canonical version of 'X.Y.dev'
__version__ = "0.1.0"

from pypots import classification
from pypots import clustering
from pypots import data
from pypots import forecasting
from pypots import imputation
from pypots import utils

__all__ = [
    "classification",
    "clustering",
    "data",
    "forecasting",
    "imputation",
    "utils",
    "__version__",
]
