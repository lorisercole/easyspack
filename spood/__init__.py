"""
Spood (spood)
"""

from .exceptions import SpecLoaderError, ValidationError, DatabaseError

__version__ = "0.1.0"
__all__ = [
    "SpecLoaderError",
    "ValidationError",
    "DatabaseError",
]

import copy, logging, os

class DebugOnlyFormatter(logging.Formatter):
    def format(self, record):
        # shallow copy so we don't mutate the original record globally
        r = copy.copy(record)
        # add a 'levelprefix' field used only in the format string
        r.levelprefix = "[DEBUG : " if r.levelno == logging.DEBUG else ""
        r.name = f"{r.name}] " if r.levelno == logging.DEBUG else ""
        return super().format(r)

# Setup logging
logging.basicConfig(level=logging.DEBUG if os.getenv("SPOOD_DEBUG") else logging.INFO)
for h in logging.root.handlers:
    h.setFormatter(DebugOnlyFormatter("%(levelprefix)s%(name)s%(message)s"))