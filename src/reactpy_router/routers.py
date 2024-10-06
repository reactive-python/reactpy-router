"""URL router implementation for ReactPy"""

from __future__ import annotations

from reactpy_router.core import create_router
from reactpy_router.resolvers import Resolver

__all__ = ["browser_router"]


browser_router = create_router(Resolver)
"""This is the recommended router for all ReactPy Router web projects.
It uses the DOM History API to update the URL and manage the history stack."""
